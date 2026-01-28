import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision.models import ResNet18_Weights
from torchvision import transforms, models
import pandas as pd
import numpy as np
from PIL import Image
import os
from sklearn.metrics import mean_squared_error, mean_absolute_error
from tqdm import tqdm

# 1. CONFIGURATION
DATA_FILE = "../data_new/weather_data_all.csv"
IMG_DIR = "../data_new/images"

BATCH_SIZE = 32
LEARNING_RATE = 0.001
EPOCHS = 10

# Subsample ratio for faster experimentation (1.0 = full data)
SUB_SAMPLE_RATIO = 0.001

if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
elif torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
else:
    DEVICE = torch.device("cpu")

print(f"Using device: {DEVICE}")


# 2. DATA LOADING (SINGLE FILE MODE)
def load_data(file_path):
    print(f"Lade Master-Dataset: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CRITICAL: {file_path} nicht gefunden! Bitte erst 'unify_data.py' ausführen.")

    df = pd.read_csv(file_path)

    # Check: Sind alle Spalten da? (Die von unify_data.py erstellt wurden)
    req_cols = ['station_id', 'temperature', 'elevation', 'latitude', 'longitude',
                'hour', 'month', 'dayofyear', 'weekday']

    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Spalten fehlen in CSV: {missing}. Ist 'unify_data.py' korrekt durchgelaufen?")

    # Speed-Up Sampling (falls gewünscht)
    if SUB_SAMPLE_RATIO < 1.0:
        print(f"✂Subsampling auf {SUB_SAMPLE_RATIO * 100}% der Daten")
        df = df.sample(frac=SUB_SAMPLE_RATIO, random_state=42).reset_index(drop=True)

    return df


# 3. DATASET
class WeatherDataset(Dataset):
    def __init__(self, df, img_dir, transform=None):
        self.df = df
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        station_id = str(row['station_id'])  # Sicherstellen, dass ID ein String ist

        # 1. BILD LADEN
        img_name = f"station_{station_id}.png"
        img_path = os.path.join(self.img_dir, img_name)

        if not os.path.exists(img_path):
            img_path_v2 = os.path.join(self.img_dir, f"{station_id}.png")
            if not os.path.exists(img_path_v2):
                raise FileNotFoundError(f"Bild fehlt für Station {station_id}!")
            img_path = img_path_v2

        image = Image.open(img_path).convert('RGB')
        if self.transform:
            image = self.transform(image)

        # 2. METADATA (7 Features)
        # Normalisierung (Wertebereich 0..1 für das neuronale Netz)
        meta = torch.tensor([
            float(row['elevation']),
            float(row['latitude']),
            float(row['longitude']),
            float(row['hour']) ,
            float(row['month']) ,
            float(row['dayofyear']) ,
            float(row['weekday'])
        ], dtype=torch.float32)

        target = torch.tensor([float(row['temperature'])], dtype=torch.float32)

        return image, meta, target, row['time']


# 4. MODEL (512 Image + 7 Meta)
class MultimodalModel(nn.Module):
    def __init__(self):
        super(MultimodalModel, self).__init__()

        self.cnn = models.resnet18(weights=ResNet18_Weights.DEFAULT)
        self.cnn.fc = nn.Identity()  # Output hier: 512 Features

        self.cnn_bottleneck = nn.Sequential(
            nn.Linear(512, 16),
            nn.ReLU(),
            nn.Dropout(0.1)
        )

        self.fc_head = nn.Sequential(
            nn.Linear(16 + 7, 64),
            nn.ReLU(),
            nn.Linear(64, 1)  # Output: Temperatur
        )

    def forward(self, img, meta):
        feat = self.cnn(img)
        feat = feat.view(feat.size(0), -1)

        feat = self.cnn_bottleneck(feat)

        combined = torch.cat((feat, meta), dim=1)

        return self.fc_head(combined)


# 5. TRAINING LOOP (LOO-CV)
def main():
    # 1. Daten laden (Single File)
    full_df = load_data(DATA_FILE)

    stations = full_df['station_id'].unique()
    print(f"Daten bereit: {len(full_df)} Zeilen, {len(stations)} Stationen.")

    tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    all_preds_df = []

    # Leave-One-Station-Out Loop
    for i, test_station in enumerate(stations):
        print(f"ROUND {i + 1}/{len(stations)}: Hold-out Station '{test_station}'")

        # Split based on station_id column
        train_df = full_df[full_df['station_id'] != test_station]
        test_df = full_df[full_df['station_id'] == test_station]

        if len(test_df) == 0:
            print("Skipping empty test station.")
            continue

        # DataLoaders
        train_ds = WeatherDataset(train_df, IMG_DIR, tf)
        test_ds = WeatherDataset(test_df, IMG_DIR, tf)

        train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
        test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

        # Model Init
        model = MultimodalModel().to(DEVICE)
        opt = optim.Adam(model.parameters(), lr=LEARNING_RATE)
        loss_fn = nn.MSELoss()

        # Training
        model.train()
        for epoch in range(EPOCHS):
            loop = tqdm(train_loader, desc=f"Ep {epoch + 1}/{EPOCHS}", leave=False)
            epoch_losses = []

            for img, meta, y, _ in loop:
                img, meta, y = img.to(DEVICE), meta.to(DEVICE), y.to(DEVICE)

                opt.zero_grad()
                pred = model(img, meta)
                loss = loss_fn(pred, y)
                loss.backward()
                opt.step()

                epoch_losses.append(loss.item())
                loop.set_postfix(loss=np.mean(epoch_losses))

        # Evaluation (Validation on Hold-out Station)
        model.eval()
        true_vals, pred_vals, timestamps = [], [], []

        with torch.no_grad():
            for img, meta, y, time_batch in test_loader:
                img, meta, y = img.to(DEVICE), meta.to(DEVICE), y.to(DEVICE)
                pred = model(img, meta)

                true_vals.extend(y.cpu().numpy().flatten())
                pred_vals.extend(pred.cpu().numpy().flatten())
                timestamps.extend(time_batch)

        rmse_val = np.sqrt(mean_squared_error(true_vals, pred_vals))
        print(f"  Station {test_station} RMSE: {rmse_val:.4f}°C")

        # Ergebnisse speichern
        df_res = pd.DataFrame({
            'station_id': test_station,
            'time': timestamps,
            'true_temp': true_vals,
            'pred_temp': pred_vals
        })
        all_preds_df.append(df_res)

    # FINAL EVALUATION
    if not all_preds_df:
        print("Keine Vorhersagen generiert.")
        return

    final_df = pd.concat(all_preds_df, ignore_index=True)
    final_df.to_csv("cnn_results_final.csv", index=False)

    global_rmse = np.sqrt(mean_squared_error(final_df['true_temp'], final_df['pred_temp']))
    global_mae = mean_absolute_error(final_df['true_temp'], final_df['pred_temp'])

    print("FINAL CNN RESULTS (Unified Data)")
    print(f"Global RMSE: {global_rmse:.4f}")
    print(f"Global MAE : {global_mae:.4f}")
    print("Predictions saved to 'cnn_results_final.csv'")


if __name__ == "__main__":
    main()