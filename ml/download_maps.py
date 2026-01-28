import pandas as pd
import numpy as np
import os
import math
import requests
import time
from PIL import Image
from io import BytesIO
from tqdm import tqdm

# 1. CONFIGURATION
# Pfad zur Master-Datei (Neue Struktur)
DATA_FILE = "data_new/weather_data_all.csv"
# Speicherort für Bilder
IMAGES_DIR = "data_new/images"

# Zoom Level
# 13 = Stadtteil, 15 = Detail, 19 = Max Zoom (nur Hausdach)
# Empfehlung für CNNs: 16 oder 17 (zeigt Umgebung/Vegetation)
ZOOM_LEVEL = 18

print(f"Lade Stationen aus: {os.path.abspath(DATA_FILE)}")
print(f"Speichere Bilder in: {os.path.abspath(IMAGES_DIR)}")

# Ordner erstellen
os.makedirs(IMAGES_DIR, exist_ok=True)


# 2. MATH (Lat/Lon -> Tile URL)
def deg2num(lat_deg, lon_deg, zoom):
    """
    Konvertiert Latitude/Longitude in x/y Kachel-Koordinaten für OSM.
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def download_tile(station_id, lat, lon):
    """
    Lädt die Kachel von OpenStreetMap herunter.
    """
    xtile, ytile = deg2num(lat, lon, ZOOM_LEVEL)

    # URL Format für OpenStreetMap (Standard Server)
    url = f"https://tile.openstreetmap.org/{ZOOM_LEVEL}/{xtile}/{ytile}.png"

    # User-Agent setzen, sonst blockiert OSM das Skript (403 Forbidden)
    headers = {
        'User-Agent': 'ResearchProject_FH_AI/1.0 (contact: student@fh-salzburg.ac.at)'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            try:
                img = Image.open(BytesIO(response.content))
                # Optional: Auf ResNet Standard (224x224) skalieren
                img = img.resize((224, 224), Image.Resampling.LANCZOS)

                # Als RGB speichern (manche PNGs sind RGBA)
                img = img.convert('RGB')

                # Speichern
                save_path = os.path.join(IMAGES_DIR, f"station_{station_id}.png")
                img.save(save_path)
                return True
            except Exception as img_err:
                print(f"Bildfehler bei Station {station_id}: {img_err}")
                return False
        else:
            print(f"HTTP {response.status_code} bei URL: {url}")
            return False

    except Exception as e:
        print(f"Netzwerkfehler bei Station {station_id}: {e}")
        return False


# 3. MAIN LOOP
def main():
    if not os.path.exists(DATA_FILE):
        print("Master-Datei fehlt! Bitte erst 'unify_data.py' ausführen.")
        return

    # 1. Daten laden
    print("Lade CSV...")
    df = pd.read_csv(DATA_FILE)

    # 2. Einzigartige Stationen extrahieren
    # Wir brauchen nur ID, Lat, Lon -> Duplikate entfernen
    stations_df = df[['station_id', 'latitude', 'longitude']].drop_duplicates(subset=['station_id'])

    print(f"Gefunden: {len(stations_df)} einzigartige Stationen.")

    success_count = 0
    skipped_count = 0

    # 3. Loop über Stationen
    loop = tqdm(stations_df.iterrows(), total=len(stations_df), desc="Lade Bilder")

    for index, row in loop:
        station_id = int(row['station_id'])
        lat = row['latitude']
        lon = row['longitude']

        # Zieldatei prüfen
        if os.path.exists(os.path.join(IMAGES_DIR, f"station_{station_id}.png")):
            skipped_count += 1
            continue

        if pd.isna(lat) or pd.isna(lon):
            print(f"Keine Koordinaten für Station {station_id}, überspringe.")
            continue

        # Download
        if download_tile(station_id, lat, lon):
            success_count += 1

        # WICHTIG: Kurze Pause für Fair Use Policy von OSM (max 1 Req/sec)
        time.sleep(0.15)
    print(f"Neu geladen: {success_count}")
    print(f"Übersprungen (schon da): {skipped_count}")
    print(f"Bilder liegen in: {os.path.abspath(IMAGES_DIR)}")


if __name__ == "__main__":
    main()