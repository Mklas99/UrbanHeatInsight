import pandas as pd
import numpy as np
import os
import glob

# ==========================================
# 1. CONFIGURATION
# ==========================================
INPUT_FOLDER = 'weather_stations'
METADATA_FILE = 'stations_metadaten.csv'

# Output paths
OUTPUT_BASE = os.path.join('..', 'deeplearning', 'data')
OUTPUT_STATIONS = os.path.join(OUTPUT_BASE, 'stations')

# Create directory automatically
os.makedirs(OUTPUT_STATIONS, exist_ok=True)

print(f"📂 Input Folder: {INPUT_FOLDER}")
print(f"📂 Output Stations: {os.path.abspath(OUTPUT_STATIONS)}")


# ==========================================
# 2. LOAD AND MERGE DATA
# ==========================================
def preprocess():
    print("\n[1/3] Loading CSV files...")

    # 1. Find Measurement File Automatically
    search_pattern = os.path.join(INPUT_FOLDER, "Messstationen*.csv")
    found_files = glob.glob(search_pattern)

    if not found_files:
        print("❌ Error: No measurement file found starting with 'Messstationen'!")
        return

    meas_file_path = found_files[0]
    print(f"   -> Using Measurement File: {os.path.basename(meas_file_path)}")

    # Load Measurements
    # Force 'station' to string
    df_meas = pd.read_csv(meas_file_path, sep=None, engine='python')
    df_meas['station'] = df_meas['station'].astype(str)

    # Load Metadata
    # Force 'id' to string
    df_meta = pd.read_csv(os.path.join(INPUT_FOLDER, METADATA_FILE), sep=None, engine='python')
    df_meta['id'] = df_meta['id'].astype(str)

    print("\n[2/3] Merging and Cleaning...")

    # Merge measurements with metadata
    df_merged = pd.merge(df_meas, df_meta, left_on='station', right_on='id', how='inner')

    # Rename columns German -> English
    df_merged = df_merged.rename(columns={
        'tl_mittel': 'temperature',
        'Höhe [m]': 'elevation',
        'station': 'station_id',
        'Stationsname': 'station_name',
        'Länge [°E]': 'longitude',
        'Breite [°N]': 'latitude',
        'time': 'time'
    })

    # Drop rows with missing crucial data
    df_merged = df_merged.dropna(subset=['temperature', 'elevation', 'latitude', 'longitude'])

    # Select columns
    final_df = df_merged[['time', 'temperature', 'elevation', 'latitude', 'longitude', 'station_id', 'station_name']]

    unique_stations = final_df['station_id'].unique()
    print(f"   -> ✅ Successfully prepared data for {len(unique_stations)} stations.")

    # ==========================================
    # 3. SPLIT INTO FILES (NO IMAGES)
    # ==========================================
    print("\n[3/3] Saving Station CSVs...")

    count = 0
    for station_id in unique_stations:
        # Filter data for this station
        station_data = final_df[final_df['station_id'] == station_id].copy()

        # Sort by time
        station_data['time'] = pd.to_datetime(station_data['time'])
        station_data = station_data.sort_values(by='time')

        # Save CSV
        csv_filename = f"station_{station_id}.csv"
        csv_path = os.path.join(OUTPUT_STATIONS, csv_filename)
        station_data.to_csv(csv_path, index=False)

        count += 1

    print(f"\nDone! Processed {count} stations.")
    print(f"Data is ready in: {os.path.abspath(OUTPUT_STATIONS)}")


if __name__ == "__main__":
    preprocess()