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
import glob
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error

# ==========================================
# 1. CONFIGURATION
# ==========================================
STATIONS_DIR = './data/stations'
IMG_DIR = './data/images'

# Hyperparameters
BATCH_SIZE = 8
LEARNING_RATE = 0.001
EPOCHS = 5

# Device configuration (CUDA, MPS for Mac, or CPU)
if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
elif torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
else:
    DEVICE = torch.device("cpu")

print(f"Using device: {DEVICE}")


# ==========================================
# 2. DATA LOADING
# ==========================================
def load_data_from_folder(stations_dir):
    """Loads all CSV files from the folder and merges them into one DataFrame."""
    all_files = glob.glob(os.path.join(stations_dir, "*.csv"))

    if len(all_files) == 0:
        raise ValueError(f"No CSV files found in {stations_dir}!")

    dfs = []
    print(f"Reading {len(all_files)} CSV files from {stations_dir}...")

    for filename in all_files:
        try:
            df = pd.read_csv(filename)

            # Use filename as station_id (e.g., 'station_1.csv' -> 'station_1')
            station_id = os.path.basename(filename).replace('.csv', '')
            df['station_id'] = station_id

            # Check for required columns
            required_cols = ['time', 'temperature', 'elevation']
            if not all(col in df.columns for col in required_cols):
                print(f"Warning: File {filename} is missing columns. Skipping.")
                continue

            dfs.append(df)
        except Exception as e:
            print(f"Error reading file {filename}: {e}")

    if not dfs:
        raise ValueError("No valid CSV files found!")

    return pd.concat(dfs, ignore_index=True)


# ==========================================
# 3. DATASET & MODEL
# ==========================================
class WeatherDataset(Dataset):
    def __init__(self, df, img_dir, transform=None):
        self.df = df
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        # --- Load Image ---
        img_name = f"{row['station_id']}.png"
        img_path = os.path.join(self.img_dir, img_name)

        # Fallback to .jpg if .png doesn't exist
        if not os.path.exists(img_path):
            img_path = os.path.join(self.img_dir, f"{row['station_id']}.jpg")

        try:
            image = Image.open(img_path).convert('RGB')
        except (FileNotFoundError, OSError):
            # Return black image if file is missing/corrupt to prevent crash
            image = Image.new('RGB', (224, 224), color='black')

        if self.transform:
            image = self.transform(image)

        # --- Process Metadata (Time & Elevation) ---
        try:
            ts = pd.to_datetime(row['time'])
            hour_val = ts.hour
        except:
            hour_val = 12.0  # Default to noon if parsing fails

        # Normalize inputs: Elevation / 1000m, Hour / 24h
        meta = torch.tensor([
            float(row['elevation']) / 1000.0,
            float(hour_val) / 24.0
        ], dtype=torch.float32)

        target = torch.tensor([float(row['temperature'])], dtype=torch.float32)

        return image, meta, target


class MultimodalModel(nn.Module):
    def __init__(self):
        super(MultimodalModel, self).__init__()
        # Visual Backbone: ResNet18
        self.cnn = models.resnet18(weights=ResNet18_Weights.DEFAULT)
        self.cnn.fc = nn.Identity()  # Remove classification head

        # Regression Head: 512 (Image features) + 2 (Meta features)
        self.fc_head = nn.Sequential(
            nn.Linear(512 + 2, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 1)  # Output: Temperature
        )

    def forward(self, img, meta):
        features = self.cnn(img)
        features = features.view(features.size(0), -1)  # Flatten

        # Concatenate visual and metadata features
        combined = torch.cat((features, meta), dim=1)

        return self.fc_head(combined)


# ==========================================
# 4. MAIN LOOP (Leave-One-Station-Out)
# ==========================================
def main():
    # Load Data
    try:
        full_df = load_data_from_folder(STATIONS_DIR)
    except Exception as e:
        print(e)
        return

    unique_stations = full_df['station_id'].unique()
    print(f"Found {len(unique_stations)} unique stations: {unique_stations}")

    # Standard ImageNet normalization
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    global_true = []
    global_pred = []

    # Leave-One-Out Cross-Validation Loop
    for i, test_station in enumerate(unique_stations):
        print(f"\n--- ROUND {i + 1}/{len(unique_stations)}: Testing on '{test_station}' ---")

        # Split data: Hold out one station for testing, train on the rest
        test_df = full_df[full_df['station_id'] == test_station]
        train_df = full_df[full_df['station_id'] != test_station]

        train_loader = DataLoader(WeatherDataset(train_df, IMG_DIR, transform),
                                  batch_size=BATCH_SIZE, shuffle=True)
        test_loader = DataLoader(WeatherDataset(test_df, IMG_DIR, transform),
                                 batch_size=1, shuffle=False)

        # Re-initialize model for every fold (crucial for valid CV)
        model = MultimodalModel().to(DEVICE)
        optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
        criterion = nn.MSELoss()

        # Training
        model.train()
        for epoch in range(EPOCHS):
            batch_losses = []
            for img, meta, target in train_loader:
                img, meta, target = img.to(DEVICE), meta.to(DEVICE), target.to(DEVICE)

                optimizer.zero_grad()
                pred = model(img, meta)
                loss = criterion(pred, target)
                loss.backward()
                optimizer.step()
                batch_losses.append(loss.item())

            if (epoch + 1) % 5 == 0:
                print(f"  Epoch {epoch + 1}, Loss: {np.mean(batch_losses):.4f}")

        # Evaluation
        model.eval()
        station_targets = []
        station_preds = []

        with torch.no_grad():
            for img, meta, target in test_loader:
                img, meta, target = img.to(DEVICE), meta.to(DEVICE), target.to(DEVICE)
                pred = model(img, meta)

                station_targets.append(target.item())
                station_preds.append(pred.item())

        rmse_station = np.sqrt(mean_squared_error(station_targets, station_preds))
        print(f"  -> RMSE for {test_station}: {rmse_station:.2f}°C")

        global_true.extend(station_targets)
        global_pred.extend(station_preds)

    # Global Metrics
    total_rmse = np.sqrt(mean_squared_error(global_true, global_pred))
    total_mae = mean_absolute_error(global_true, global_pred)

    print("\n" + "=" * 40)
    print(f"FINAL RESULTS (Leave-One-Out CV)")
    print("=" * 40)
    print(f"RMSE: {total_rmse:.4f} °C")
    print(f"MAE:  {total_mae:.4f} °C")
    print("=" * 40)

    # Plotting
    plt.figure(figsize=(6, 6))
    plt.scatter(global_true, global_pred, alpha=0.5, label='Predictions')

    # Perfect prediction line
    min_val = min(min(global_true), min(global_pred))
    max_val = max(max(global_true), max(global_pred))
    plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Ideal')

    plt.xlabel('Measured Temperature (°C)')
    plt.ylabel('Predicted Temperature (°C)')
    plt.title(f'Spatial Generalization (RMSE: {total_rmse:.2f}°C)')
    plt.legend()
    plt.grid(True)

    plt.savefig('final_results.png')
    print("Plot saved as: final_results.png")


if __name__ == "__main__":
    main()