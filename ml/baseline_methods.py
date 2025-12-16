import re
from pathlib import Path
from typing import Optional, Tuple, Union, List

import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# -----------------------------
# Metrics
# -----------------------------

def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def print_metrics(y_true, y_pred, title: str) -> None:
    print(f"\n=== {title} ===")
    print(f"RMSE: {rmse(y_true, y_pred):.4f}")
    print(f"MAE : {mean_absolute_error(y_true, y_pred):.4f}")


# -----------------------------
# Station id parsing
# -----------------------------

def infer_station_id_from_filename(path: Union[str, Path]) -> int:
    """
    Expects filenames like: 105_105.csv, 4102_4102.csv
    Returns the leading integer station id.
    """
    name = Path(path).name
    m = re.match(r"(\d+)", name)
    if not m:
        raise ValueError(f"Could not infer station_id from filename: {name}")
    return int(m.group(1))


# -----------------------------
# Data loading
# -----------------------------

def load_station_metadata(metadata_path: str) -> pd.DataFrame:
    """
    Loads station metadata (CSV or Excel). Must contain 'station_id' and location columns.
    """
    p = Path(metadata_path)
    if not p.exists():
        raise FileNotFoundError(metadata_path)

    if p.suffix.lower() == ".csv":
        meta = pd.read_csv(p)
    elif p.suffix.lower() in [".xlsx", ".xls"]:
        meta = pd.read_excel(p)
    else:
        raise ValueError("metadata_path must be a .csv or .xlsx/.xls file")

    if "station_id" not in meta.columns:
        raise ValueError("Station metadata must contain a 'station_id' column.")

    meta["station_id"] = pd.to_numeric(meta["station_id"], errors="coerce").astype("Int64")
    meta = meta.dropna(subset=["station_id"]).copy()
    meta["station_id"] = meta["station_id"].astype(int)
    return meta


def load_hourly_station_csvs(
    folder: str,
    metadata_path: Optional[str] = None,
    file_glob: str = "*.csv",
    timestamp_column: str = "time",
) -> pd.DataFrame:
    """
    Loads all hourly station CSVs and concatenates them.
    - Skips metadata file if it is in the same folder
    - Skips non-station CSVs (filenames not starting with digits)
    - Adds station_id inferred from filename
    """
    folder_path = Path(folder)
    if not folder_path.exists():
        raise FileNotFoundError(folder)

    meta_resolved = Path(metadata_path).resolve() if metadata_path else None
    files = sorted(folder_path.glob(file_glob))
    if not files:
        raise ValueError(f"No CSV files found in {folder} matching {file_glob}")

    frames = []
    for f in files:
        if meta_resolved is not None and f.resolve() == meta_resolved:
            print(f"Skipping metadata file: {f.name}")
            continue

        if not re.match(r"^\d+", f.name):
            print(f"Skipping non-hourly file (no leading station id): {f.name}")
            continue

        df = pd.read_csv(f)
        df["station_id"] = infer_station_id_from_filename(f)

        if timestamp_column in df.columns:
            df[timestamp_column] = pd.to_datetime(df[timestamp_column], errors="coerce", utc=True)

        frames.append(df)

    if not frames:
        raise ValueError("No hourly station CSVs were loaded (all files were skipped).")

    return pd.concat(frames, ignore_index=True)


def add_time_features(
    df: pd.DataFrame,
    timestamp_column: str = "time",
    local_tz: Optional[str] = "Europe/Vienna",
) -> pd.DataFrame:
    """
    Adds time features: hour, dayofyear, month, weekday.
    Converts from UTC to local_tz if provided.
    """
    if timestamp_column not in df.columns:
        raise ValueError(f"Timestamp column '{timestamp_column}' not found.")

    if not is_datetime64_any_dtype(df[timestamp_column]):
        df[timestamp_column] = pd.to_datetime(df[timestamp_column], errors="coerce", utc=True)

    ts = df[timestamp_column]
    if getattr(ts.dt, "tz", None) is not None:
        if local_tz:
            ts = ts.dt.tz_convert(local_tz)
        ts = ts.dt.tz_localize(None)

    df["hour"] = ts.dt.hour
    df["dayofyear"] = ts.dt.dayofyear
    df["month"] = ts.dt.month
    df["weekday"] = ts.dt.weekday
    return df


# -----------------------------
# Model
# -----------------------------

def build_location_time_baseline_pipeline(numeric_features: List[str]) -> Pipeline:
    """
    Numeric-only pipeline: impute median + scale + RidgeCV.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]), numeric_features),
        ],
        remainder="drop",
    )

    reg = RidgeCV(alphas=np.logspace(-3, 3, 13))

    return Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", reg),
    ])


def run_leave_one_station_out_cv(
    data: pd.DataFrame,
    target_column: str,
    group_column: str,
    feature_columns: List[str],
) -> Tuple[Pipeline, pd.DataFrame]:
    """
    Leave-One-Station-Out evaluation using LeaveOneGroupOut (groups=station_id).
    Returns fitted model on all data and a dataframe with LOSO predictions.
    """
    needed = set(feature_columns + [target_column, group_column])
    missing = [c for c in needed if c not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = data.dropna(subset=[target_column, group_column]).copy()
    df[group_column] = pd.to_numeric(df[group_column], errors="coerce").astype("Int64")
    df = df.dropna(subset=[group_column]).copy()
    df[group_column] = df[group_column].astype(int)

    X = df[feature_columns].copy()
    y = df[target_column].values
    groups = df[group_column].values

    model = build_location_time_baseline_pipeline(numeric_features=feature_columns)

    logo = LeaveOneGroupOut()
    y_pred = cross_val_predict(model, X, y, cv=logo, groups=groups)

    print_metrics(y, y_pred, title="Location+Time Baseline (Leave-One-Station-Out)")

    # Fit final model on all available data
    model.fit(X, y)

    out = df.copy()
    out[f"{target_column}_loso_pred"] = y_pred
    out[f"{target_column}_error"] = out[f"{target_column}_loso_pred"] - out[target_column]
    return model, out


# -----------------------------
# Main
# -----------------------------

if __name__ == "__main__":
    # Paths (adapt if needed)
    METADATA_PATH = "../data/weather_stations/stations_vienna.csv"
    HOURLY_FOLDER = "../data/weather_stations"

    # Target to predict (your hourly data has 'tl' for air temperature)
    TARGET_COLUMN = "tl"

    # Time column in hourly CSVs
    TIMESTAMP_COLUMN = "time"

    # Columns from metadata for location
    LON_COL = "Länge [°E]"
    LAT_COL = "Breite [°N]"
    ELEV_COL = "Höhe [m]"

    # 1) Load station metadata
    meta = load_station_metadata(METADATA_PATH)

    # 2) Load hourly station CSVs
    hourly = load_hourly_station_csvs(
        HOURLY_FOLDER,
        metadata_path=METADATA_PATH,
        file_glob="*.csv",
        timestamp_column=TIMESTAMP_COLUMN
    )

    # 3) Merge hourly with metadata
    data = hourly.merge(meta, on="station_id", how="left")

    # 4) Add time features (Vienna local time) and drop raw timestamp
    data = add_time_features(data, timestamp_column=TIMESTAMP_COLUMN, local_tz="Europe/Vienna")
    data = data.drop(columns=[TIMESTAMP_COLUMN])

    # 5) Define the ONLY features we use (available everywhere)
    FEATURE_COLUMNS = [
        LON_COL,
        LAT_COL,
        ELEV_COL,
        "hour",
        "dayofyear",
        "month",
        "weekday",
    ]

    print("\nFeature columns used (location + time only):")
    print(FEATURE_COLUMNS)

    # 6) Run LOSO baseline
    model, df_with_preds = run_leave_one_station_out_cv(
        data=data,
        target_column=TARGET_COLUMN,
        group_column="station_id",
        feature_columns=FEATURE_COLUMNS,
    )

    # 7) Per-station bias summary (mean)
    per_station = (
        df_with_preds.groupby("station_id")[[TARGET_COLUMN, f"{TARGET_COLUMN}_loso_pred", f"{TARGET_COLUMN}_error"]]
        .mean()
        .sort_index()
    )

    print("\nPer-station mean results:")
    print(per_station)
