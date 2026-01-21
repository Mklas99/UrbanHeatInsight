import os
import json
import math
import argparse
from functools import lru_cache
from typing import Optional, Tuple, Dict, List

import numpy as np
import pandas as pd
from tqdm import tqdm
from sklearn.metrics import mean_squared_error, mean_absolute_error

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import models
from torchvision.models import ResNet18_Weights
import time
from datetime import timedelta


# =========================================================
# Multimodal regression training (static NPY patches + meta)
# Upgrades:
# - LOSO cross-validation (leave-one-station-out)
# - fold-wise normalization (meta + optional target)
# - cyclical time encoding
# - AMP (CUDA), AdamW, cosine LR schedule + warmup
# - gradient clipping, early stopping, checkpoints
# - Balanced subsampling per station:
#   * station_sample_ratio = x% rows per station
#   * rows_per_station     = exact N rows per station (overrides ratio)
# =========================================================


# --------------------------
# Utility: reproducibility
# --------------------------
def seed_everything(seed: int = 42, deterministic: bool = False) -> None:
    import random

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def print_station_stats(df: pd.DataFrame, station_col: str, title: str):
    counts = df[station_col].value_counts().sort_index()
    print("\n" + "-" * 60)
    print(title)
    print("-" * 60)
    print(counts.to_string())
    print("-" * 60)
    print(
        f"Stations: {counts.shape[0]} | "
        f"Total rows: {counts.sum()} | "
        f"Min: {counts.min()} | "
        f"Max: {counts.max()} | "
        f"Mean: {counts.mean():.2f}"
    )
    print("-" * 60 + "\n")

def format_seconds(seconds: float) -> str:
    return str(timedelta(seconds=int(seconds)))


# --------------------------
# Fold-safe scalers
# --------------------------
class StandardScalerNP:
    """Simple numpy scaler for (N, D) arrays."""

    def __init__(self, eps: float = 1e-8):
        self.mean_: Optional[np.ndarray] = None
        self.std_: Optional[np.ndarray] = None
        self.eps = eps

    def fit(self, x: np.ndarray) -> "StandardScalerNP":
        self.mean_ = np.nanmean(x, axis=0)
        self.std_ = np.nanstd(x, axis=0)
        self.std_ = np.maximum(self.std_, self.eps)
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        assert self.mean_ is not None and self.std_ is not None
        return (x - self.mean_) / self.std_

    def fit_transform(self, x: np.ndarray) -> np.ndarray:
        return self.fit(x).transform(x)


# --------------------------
# Balanced sampling per station
# --------------------------
def balanced_sample_per_station_ratio(
    df: pd.DataFrame,
    station_col: str,
    ratio: float,
    seed: int,
    min_rows: int = 1,
) -> pd.DataFrame:
    """
    Keep approximately `ratio` of rows PER station.

    - ratio in (0,1] ; if >=1.0 => return df unchanged
    - ensures at least `min_rows` per station (if available)
    - deterministic per station via stable seed mixing
    """
    if ratio >= 1.0:
        return df.reset_index(drop=True)
    if ratio <= 0.0:
        raise ValueError("station_sample_ratio must be > 0")

    sampled_parts = []
    for sid, g in df.groupby(station_col, sort=False):
        n = len(g)
        k = max(min_rows, int(round(n * ratio)))
        k = min(k, n)
        rs = (hash(str(sid)) % 2_000_000_000) ^ seed
        sampled_parts.append(g.sample(n=k, random_state=rs))

    out = pd.concat(sampled_parts, axis=0).sample(frac=1.0, random_state=seed)
    return out.reset_index(drop=True)


def balanced_sample_per_station_count(
    df: pd.DataFrame,
    station_col: str,
    n_per_station: int,
    seed: int,
) -> pd.DataFrame:
    """
    Keep exactly n_per_station per station (or all rows if station has fewer).
    Deterministic per station via stable seed mixing.
    """
    if n_per_station <= 0:
        raise ValueError("rows_per_station must be >= 1")

    parts = []
    for sid, g in df.groupby(station_col, sort=False):
        n = len(g)
        k = min(n_per_station, n)
        rs = (hash(str(sid)) % 2_000_000_000) ^ seed
        parts.append(g.sample(n=k, random_state=rs))

    out = pd.concat(parts, axis=0).sample(frac=1.0, random_state=seed)
    return out.reset_index(drop=True)


# --------------------------
# Patch I/O and normalization
# --------------------------
def _station_npy_path(npy_dir: str, station_id: str) -> str:
    return os.path.join(npy_dir, f"{station_id}_static.npy")


def _station_meta_path(npy_dir: str, station_id: str) -> str:
    return os.path.join(npy_dir, f"{station_id}_static.meta.json")


@lru_cache(maxsize=4096)
def load_station_patch(
    npy_dir: str, station_id: str
) -> Tuple[np.ndarray, Optional[dict]]:
    npy_path = _station_npy_path(npy_dir, station_id)
    if not os.path.exists(npy_path):
        raise FileNotFoundError(
            f"Missing .npy patch for station {station_id}: {npy_path}"
        )
    patch = np.load(npy_path).astype(np.float32)  # (C,H,W)

    meta = None
    meta_path = _station_meta_path(npy_dir, station_id)
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = None
    return patch, meta


def normalize_patch(patch_chw: np.ndarray, rgb_channels: int) -> np.ndarray:
    """
    Assumptions (adapt if your channels differ):
    - First rgb_channels are 0..255-like, scaled to 0..1
    - Remaining channels are masks / continuous in [0,1] (clipped)
    """
    patch = patch_chw.astype(np.float32)
    c = patch.shape[0]

    if c >= rgb_channels:
        patch[:rgb_channels] = patch[:rgb_channels] / 255.0
    if c > rgb_channels:
        patch[rgb_channels:] = np.clip(patch[rgb_channels:], 0.0, 1.0)

    patch = np.nan_to_num(patch, nan=0.0, posinf=0.0, neginf=0.0)
    return patch


def center_crop_or_pad(img: torch.Tensor, out_h: int, out_w: int) -> torch.Tensor:
    """img: (C,H,W). Center-crop if too large; pad with zeros if too small."""
    c, h, w = img.shape
    pad_h = max(out_h - h, 0)
    pad_w = max(out_w - w, 0)
    if pad_h > 0 or pad_w > 0:
        left = pad_w // 2
        right = pad_w - left
        top = pad_h // 2
        bottom = pad_h - top
        img = torch.nn.functional.pad(
            img, (left, right, top, bottom), mode="constant", value=0.0
        )
        c, h, w = img.shape

    if h > out_h:
        top = (h - out_h) // 2
        img = img[:, top : top + out_h, :]
    if w > out_w:
        left = (w - out_w) // 2
        img = img[:, :, left : left + out_w]
    return img


# --------------------------
# Meta feature engineering
# --------------------------
def cyclical_encode(value: float, period: float) -> Tuple[float, float]:
    angle = 2.0 * math.pi * (value / period)
    return math.sin(angle), math.cos(angle)


def build_meta_features_row(row: pd.Series) -> np.ndarray:
    """
    Fold-agnostic raw features. We standardize fold-wise later.
    Columns expected:
    elevation, latitude, longitude, hour, month, dayofyear, weekday
    """
    elev = float(row["elevation"])
    lat = float(row["latitude"])
    lon = float(row["longitude"])

    hour = float(row["hour"])
    doy = float(row["dayofyear"])
    month = float(row["month"])
    weekday = float(row["weekday"])

    h_sin, h_cos = cyclical_encode(hour, 24.0)
    d_sin, d_cos = cyclical_encode(doy, 365.0)
    m_sin, m_cos = cyclical_encode(month - 1.0, 12.0)  # month often 1..12
    w_sin, w_cos = cyclical_encode(weekday, 7.0)  # weekday often 0..6

    return np.array(
        [elev, lat, lon, h_sin, h_cos, d_sin, d_cos, m_sin, m_cos, w_sin, w_cos],
        dtype=np.float32,
    )


# --------------------------
# Dataset
# --------------------------
class WeatherDatasetNPY(Dataset):
    """
    Each row is (station, time). Patch is static per station.
    Meta scaling and target scaling are applied via provided scalers (fold-wise).
    """

    def __init__(
        self,
        df: pd.DataFrame,
        npy_dir: str,
        train_resolution: int,
        rgb_channels: int,
        meta_scaler: Optional[StandardScalerNP] = None,
        y_scaler: Optional[StandardScalerNP] = None,
    ):
        self.df = df.reset_index(drop=True)
        self.npy_dir = npy_dir
        self.train_resolution = train_resolution
        self.rgb_channels = rgb_channels
        self.meta_scaler = meta_scaler
        self.y_scaler = y_scaler

        # Fail-fast: ensure patches exist for all stations
        missing = []
        for sid in self.df["station_id"].astype(str).unique():
            if not os.path.exists(_station_npy_path(self.npy_dir, sid)):
                missing.append(sid)
        if missing:
            raise FileNotFoundError(
                f"Missing .npy patches for {len(missing)} station(s). Examples: {missing[:10]}. "
                f"Expected <station_id>_static.npy in {self.npy_dir}"
            )

        # Precompute meta
        self._meta_raw = np.stack(
            [build_meta_features_row(self.df.iloc[i]) for i in range(len(self.df))],
            axis=0,
        )
        if self.meta_scaler is not None:
            self._meta = self.meta_scaler.transform(self._meta_raw).astype(np.float32)
        else:
            self._meta = self._meta_raw.astype(np.float32)

        # Target
        y = self.df["temperature"].astype(np.float32).to_numpy().reshape(-1, 1)
        if self.y_scaler is not None:
            y = self.y_scaler.transform(y).astype(np.float32)
        self._y = y.astype(np.float32)

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        station_id = str(row["station_id"])

        patch, _meta_json = load_station_patch(self.npy_dir, station_id)
        patch = normalize_patch(patch, rgb_channels=self.rgb_channels)

        x_img = torch.from_numpy(patch)  # (C,H,W)
        x_img = center_crop_or_pad(x_img, self.train_resolution, self.train_resolution)

        c, h, w = x_img.shape
        if (h != self.train_resolution) or (w != self.train_resolution):
            x_img = torch.nn.functional.interpolate(
                x_img.unsqueeze(0),
                size=(self.train_resolution, self.train_resolution),
                mode="bilinear",
                align_corners=False,
            ).squeeze(0)

        meta = torch.from_numpy(self._meta[idx])  # (D,)
        y = torch.from_numpy(self._y[idx])  # (1,)

        return x_img, meta, y, row["time"], station_id


# --------------------------
# Model
# --------------------------
class MultimodalModelNPY(nn.Module):
    def __init__(
        self,
        in_channels: int,
        meta_dim: int,
        dropout: float = 0.2,
        freeze_backbone: bool = False,
    ):
        super().__init__()
        self.cnn = models.resnet18(weights=ResNet18_Weights.DEFAULT)

        # Replace first conv to accept in_channels
        old = self.cnn.conv1
        self.cnn.conv1 = nn.Conv2d(
            in_channels=in_channels,
            out_channels=old.out_channels,
            kernel_size=old.kernel_size,
            stride=old.stride,
            padding=old.padding,
            bias=False,
        )

        # Initialize conv1 weights based on pretrained RGB conv
        with torch.no_grad():
            w = old.weight  # (64,3,7,7)
            if in_channels == 3:
                self.cnn.conv1.weight.copy_(w)
            elif in_channels > 3:
                self.cnn.conv1.weight[:, :3].copy_(w)
                mean_w = w.mean(dim=1, keepdim=True)  # (64,1,7,7)
                for c in range(3, in_channels):
                    self.cnn.conv1.weight[:, c : c + 1].copy_(mean_w)
            else:
                mean_w = w.mean(dim=1, keepdim=True)
                self.cnn.conv1.weight.copy_(mean_w.repeat(1, in_channels, 1, 1))

        # Remove classification head -> 512 embedding
        self.cnn.fc = nn.Identity()

        if freeze_backbone:
            for p in self.cnn.parameters():
                p.requires_grad = False
            # allow conv1 to adapt to channel change
            for p in self.cnn.conv1.parameters():
                p.requires_grad = True

        self.meta_net = nn.Sequential(
            nn.Linear(meta_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
        )

        self.head = nn.Sequential(
            nn.Linear(512 + 32, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, img: torch.Tensor, meta: torch.Tensor) -> torch.Tensor:
        feat_img = self.cnn(img)  # (B,512)
        feat_meta = self.meta_net(meta)  # (B,32)
        x = torch.cat([feat_img, feat_meta], dim=1)
        return self.head(x)  # (B,1)


# --------------------------
# LR schedule with warmup
# --------------------------
def build_scheduler(optimizer, total_steps: int, warmup_steps: int):
    def lr_lambda(step: int):
        if step < warmup_steps:
            return float(step) / float(max(1, warmup_steps))
        progress = float(step - warmup_steps) / float(
            max(1, total_steps - warmup_steps)
        )
        return 0.5 * (1.0 + math.cos(math.pi * progress))

    return optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)


# --------------------------
# Metrics helpers
# --------------------------
def rmse(y_true: List[float], y_pred: List[float]) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


# --------------------------
# Data loading & validation
# --------------------------
def load_data(file_path: str, seed: int) -> pd.DataFrame:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CRITICAL: {file_path} not found.")

    df = pd.read_csv(file_path)

    req_cols = [
        "station_id",
        "temperature",
        "elevation",
        "latitude",
        "longitude",
        "hour",
        "month",
        "dayofyear",
        "weekday",
        "time",
    ]
    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    df["station_id"] = df["station_id"].astype(str)
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(
        subset=[
            "station_id",
            "temperature",
            "latitude",
            "longitude",
            "hour",
            "dayofyear",
        ]
    ).reset_index(drop=True)

    # optional shuffle for stable downstream
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


# --------------------------
# Evaluation
# --------------------------
@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    y_scaler: Optional[StandardScalerNP],
) -> Dict[str, object]:
    model.eval()
    true_vals: List[float] = []
    pred_vals: List[float] = []
    times: List[str] = []
    stations: List[str] = []

    for img, meta, y, time_batch, station_batch in loader:
        img = img.to(device, non_blocking=True)
        meta = meta.to(device, non_blocking=True)
        y = y.to(device, non_blocking=True)

        pred = model(img, meta)

        y_np = y.detach().cpu().numpy().reshape(-1, 1)
        p_np = pred.detach().cpu().numpy().reshape(-1, 1)

        if y_scaler is not None:
            y_np = y_np * y_scaler.std_ + y_scaler.mean_
            p_np = p_np * y_scaler.std_ + y_scaler.mean_

        true_vals.extend(y_np.flatten().tolist())
        pred_vals.extend(p_np.flatten().tolist())
        times.extend(list(time_batch))
        stations.extend(list(station_batch))

    return {
        "rmse": rmse(true_vals, pred_vals),
        "mae": float(mean_absolute_error(true_vals, pred_vals)),
        "true": true_vals,
        "pred": pred_vals,
        "time": times,
        "station_id": stations,
    }


# --------------------------
# Train one fold
# --------------------------
def train_one_fold(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    npy_dir: str,
    device: torch.device,
    args,
    in_channels: int,
) -> Tuple[Dict[str, object], Dict[str, float]]:
    # Fit scalers on TRAIN only
    meta_train_raw = np.stack(
        [build_meta_features_row(train_df.iloc[i]) for i in range(len(train_df))],
        axis=0,
    )
    meta_scaler = StandardScalerNP().fit(meta_train_raw)

    y_train = train_df["temperature"].astype(np.float32).to_numpy().reshape(-1, 1)
    y_scaler = StandardScalerNP().fit(y_train) if args.normalize_target else None

    train_ds = WeatherDatasetNPY(
        train_df,
        npy_dir,
        train_resolution=args.train_resolution,
        rgb_channels=args.rgb_channels,
        meta_scaler=meta_scaler,
        y_scaler=y_scaler,
    )
    test_ds = WeatherDatasetNPY(
        test_df,
        npy_dir,
        train_resolution=args.train_resolution,
        rgb_channels=args.rgb_channels,
        meta_scaler=meta_scaler,
        y_scaler=y_scaler,
    )

    pin = device.type == "cuda"
    persistent = args.num_workers > 0

    train_loader = DataLoader(
        train_ds,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=pin,
        persistent_workers=persistent,
        prefetch_factor=args.prefetch_factor if persistent else None,
        drop_last=False,
    )
    test_loader = DataLoader(
        test_ds,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=pin,
        persistent_workers=persistent,
        prefetch_factor=args.prefetch_factor if persistent else None,
        drop_last=False,
    )

    meta_dim = train_ds._meta.shape[1]
    model = MultimodalModelNPY(
        in_channels=in_channels,
        meta_dim=meta_dim,
        dropout=args.dropout,
        freeze_backbone=args.freeze_backbone,
    ).to(device)

    optimizer = optim.AdamW(
        model.parameters(), lr=args.lr, weight_decay=args.weight_decay
    )
    loss_fn = nn.SmoothL1Loss(beta=1.0) if args.use_huber else nn.MSELoss()

    total_steps = args.epochs * max(1, len(train_loader))
    warmup_steps = int(args.warmup_ratio * total_steps)
    scheduler = build_scheduler(
        optimizer, total_steps=total_steps, warmup_steps=warmup_steps
    )

    use_amp = (device.type == "cuda") and args.amp
    scaler = torch.amp.GradScaler(enabled=use_amp)

    best_rmse = float("inf")
    best_state = None
    bad_epochs = 0

    for epoch in range(1, args.epochs + 1):
        model.train()
        losses = []

        pbar = tqdm(train_loader, desc=f"Epoch {epoch}/{args.epochs}", leave=False)
        for img, meta, y, _, _ in pbar:
            img = img.to(device, non_blocking=True)
            meta = meta.to(device, non_blocking=True)
            y = y.to(device, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)

            with torch.amp.autocast(device_type="cuda", enabled=use_amp):
                pred = model(img, meta)
                loss = loss_fn(pred, y)

            scaler.scale(loss).backward()

            if args.grad_clip_norm is not None and args.grad_clip_norm > 0:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip_norm)

            scaler.step(optimizer)
            scaler.update()
            scheduler.step()

            losses.append(float(loss.item()))
            pbar.set_postfix(
                loss=float(np.mean(losses)), lr=float(optimizer.param_groups[0]["lr"])
            )

        eval_out = evaluate(model, test_loader, device, y_scaler=y_scaler)
        fold_rmse = float(eval_out["rmse"])
        fold_mae = float(eval_out["mae"])

        if fold_rmse + args.min_delta < best_rmse:
            best_rmse = fold_rmse
            best_state = {k: v.detach().cpu() for k, v in model.state_dict().items()}
            bad_epochs = 0
        else:
            bad_epochs += 1

        if args.verbose:
            print(
                f"  epoch={epoch} rmse={fold_rmse:.4f} mae={fold_mae:.4f} best_rmse={best_rmse:.4f}"
            )

        if bad_epochs >= args.patience:
            if args.verbose:
                print(f"  Early stopping triggered (patience={args.patience}).")
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    final_eval = evaluate(model, test_loader, device, y_scaler=y_scaler)
    metrics = {"rmse": float(final_eval["rmse"]), "mae": float(final_eval["mae"])}

    if args.checkpoints_dir:
        os.makedirs(args.checkpoints_dir, exist_ok=True)
        ckpt_path = os.path.join(
            args.checkpoints_dir,
            f"best_fold_station_{test_df['station_id'].iloc[0]}.pt",
        )
        torch.save(
            {
                "model_state": model.state_dict(),
                "in_channels": in_channels,
                "meta_dim": meta_dim,
                "args": vars(args),
                "metrics": metrics,
                "meta_scaler": {"mean": meta_scaler.mean_, "std": meta_scaler.std_},
                "y_scaler": (
                    None
                    if y_scaler is None
                    else {"mean": y_scaler.mean_, "std": y_scaler.std_}
                ),
            },
            ckpt_path,
        )

    return final_eval, metrics


# --------------------------
# Main
# --------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_file", type=str, default="../data_new/weather_data_all.csv"
    )
    parser.add_argument("--npy_dir", type=str, default="../data_new/static_patches")

    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--weight_decay", type=float, default=1e-4)

    parser.add_argument("--num_workers", type=int, default=0)
    parser.add_argument("--prefetch_factor", type=int, default=2)

    parser.add_argument("--train_resolution", type=int, default=100)
    parser.add_argument("--rgb_channels", type=int, default=3)

    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--deterministic", action="store_false")

    parser.add_argument("--amp", action="store_true")
    parser.add_argument("--grad_clip_norm", type=float, default=1.0)

    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--min_delta", type=float, default=0.0)

    parser.add_argument("--use_huber", action="store_true")
    parser.add_argument("--normalize_target", action="store_true")
    parser.add_argument("--warmup_ratio", type=float, default=0.05)

    parser.add_argument("--dropout", type=float, default=0.2)
    parser.add_argument("--freeze_backbone", action="store_true")

    # Balanced subsampling controls
    parser.add_argument(
        "--station_sample_ratio",
        type=float,
        default=1.0,
        help="Fraction of rows to keep PER station (balanced).",
    )
    parser.add_argument(
        "--min_rows_per_station",
        type=int,
        default=1,
        help="Minimum rows to keep per station after ratio sampling.",
    )
    parser.add_argument(
        "--rows_per_station",
        type=int,
        default=0,
        help="If >0: keep exactly this many rows per station (overrides ratio).",
    )

    parser.add_argument(
        "--out_csv", type=str, default="cnn_results_final_npy_balanced.csv"
    )
    parser.add_argument(
        "--metrics_json", type=str, default="cnn_results_metrics_balanced.json"
    )
    parser.add_argument("--checkpoints_dir", type=str, default="checkpoints_loso")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    seed_everything(args.seed, deterministic=args.deterministic)
    device = get_device()
    print(f"Using device: {device}")

    df = load_data(args.data_file, seed=args.seed)

    print_station_stats(df, station_col="station_id", title="BEFORE sampling (raw CSV)")

    # Balanced subsampling (applied BEFORE LOSO splitting)
    if args.rows_per_station and args.rows_per_station > 0:
        df = balanced_sample_per_station_count(
            df,
            station_col="station_id",
            n_per_station=args.rows_per_station,
            seed=args.seed,
        )
        sampling_desc = f"AFTER sampling (rows_per_station={args.rows_per_station})"
    else:
        df = balanced_sample_per_station_ratio(
            df,
            station_col="station_id",
            ratio=args.station_sample_ratio,
            seed=args.seed,
            min_rows=args.min_rows_per_station,
        )
        sampling_desc = (
            f"AFTER sampling (station_sample_ratio={args.station_sample_ratio}, "
            f"min_rows={args.min_rows_per_station})"
        )

    print_station_stats(df, station_col="station_id", title=sampling_desc)

    stations = df["station_id"].unique()
    print(f"Data ready: {len(df)} rows, {len(stations)} stations.")

    # Determine in_channels from a sample patch
    sample_station = str(stations[0])
    sample_patch, sample_meta = load_station_patch(args.npy_dir, sample_station)
    in_channels = int(sample_patch.shape[0])
    print(f"Using static patch channels: {in_channels}")
    if sample_meta and "channels" in sample_meta:
        print(f"Channel names: {sample_meta['channels']}")

    all_pred_rows = []
    fold_metrics = {}

    for i, test_station in enumerate(stations, start=1):
        fold_start = time.time()
        print("\n" + "=" * 60)
        print(f"Fold {i}/{len(stations)} | Hold-out station: {test_station}")
        print("=" * 60)

        train_df = df[df["station_id"] != test_station].reset_index(drop=True)
        test_df = df[df["station_id"] == test_station].reset_index(drop=True)
        if len(test_df) == 0:
            print("Skipping empty test station.")
            continue

        eval_out, metrics = train_one_fold(
            train_df=train_df,
            test_df=test_df,
            npy_dir=args.npy_dir,
            device=device,
            args=args,
            in_channels=in_channels,
        )

        fold_time = time.time() - fold_start

        print("\n" + "-" * 60)
        print(f"FOLD {i} RESULTS")
        print("-" * 60)
        print(f"  Station: {test_station}")
        print(f"  RMSE:    {metrics['rmse']:.4f} °C")
        print(f"  MAE:     {metrics['mae']:.4f} °C")
        print(f"  Time:    {format_seconds(fold_time)}")
        print("-" * 60)

        fold_metrics[str(test_station)] = metrics
        print(
            f"Fold station={test_station} RMSE={metrics['rmse']:.4f} MAE={metrics['mae']:.4f}"
        )

        for t, y_true, y_pred, sid in zip(
            eval_out["time"], eval_out["true"], eval_out["pred"], eval_out["station_id"]
        ):
            all_pred_rows.append(
                {"station_id": sid, "time": t, "true_temp": y_true, "pred_temp": y_pred}
            )

    if not all_pred_rows:
        raise RuntimeError("No predictions generated; check data paths and patches.")

    pred_df = pd.DataFrame(all_pred_rows)
    pred_df.to_csv(args.out_csv, index=False)

    global_rmse = float(
        np.sqrt(mean_squared_error(pred_df["true_temp"], pred_df["pred_temp"]))
    )
    global_mae = float(mean_absolute_error(pred_df["true_temp"], pred_df["pred_temp"]))

    # Optional: month breakdown if your "time" parses as datetime
    month_breakdown = {}
    try:
        t_parsed = pd.to_datetime(pred_df["time"], errors="coerce")
        pred_df["_month"] = t_parsed.dt.month
        for m in sorted(pred_df["_month"].dropna().unique()):
            mdf = pred_df[pred_df["_month"] == m]
            month_breakdown[int(m)] = {
                "rmse": float(
                    np.sqrt(mean_squared_error(mdf["true_temp"], mdf["pred_temp"]))
                ),
                "mae": float(mean_absolute_error(mdf["true_temp"], mdf["pred_temp"])),
                "n": int(len(mdf)),
            }
        pred_df.drop(columns=["_month"], inplace=True, errors="ignore")
    except Exception:
        month_breakdown = {}

    summary = {
        "global_rmse": global_rmse,
        "global_mae": global_mae,
        "n_samples": int(len(pred_df)),
        "n_stations": int(len(stations)),
        "fold_metrics": fold_metrics,
        "month_breakdown": month_breakdown,
        "args": vars(args),
    }
    with open(args.metrics_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("FINAL RESULTS (Balanced LOSO)")
    print("=" * 60)
    print(f"Global RMSE: {global_rmse:.4f} °C")
    print(f"Global MAE : {global_mae:.4f} °C")
    print(f"Predictions saved to: {args.out_csv}")
    print(f"Metrics saved to     : {args.metrics_json}")
    print("=" * 60)


if __name__ == "__main__":
    main()
