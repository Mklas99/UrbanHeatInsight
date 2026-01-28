import pandas as pd
import glob
import os
from tqdm import tqdm

# KONFIGURATION
# Pfad Rohdaten
INPUT_DIR = "data_new/weather_stations"
# Metadaten-Datei
METADATA_FILE = "stations_vienna.csv"
# Ziel-Datei
OUTPUT_FILE = "data_new/weather_data_all.csv"


def create_master_dataset():
    print("Starte Data Unification & Feature Engineering...")

    # 1. METADATEN LADEN (Koordinaten)
    meta_path = os.path.join(INPUT_DIR, METADATA_FILE)
    print(f"📖 Lade Metadaten von: {METADATA_FILE}")

    try:
        df_meta = pd.read_csv(meta_path)
    except Exception as e:
        print(f"Fehler beim Lesen der Metadaten: {e}")
        return

    # Spalten umbenennen
    rename_map = {
        'id': 'station_id',
        'Länge [°E]': 'longitude',
        'Breite [°N]': 'latitude',
        'Höhe [m]': 'elevation'
    }
    df_meta = df_meta.rename(columns=rename_map)

    # Doppelte Spaltennamen entfernen
    df_meta = df_meta.loc[:, ~df_meta.columns.duplicated()]

    # Nur die Spalten behalten, die wir wirklich brauchen und auf existenz prüfen
    keep_cols = ['station_id', 'longitude', 'latitude', 'elevation']
    keep_cols = [c for c in keep_cols if c in df_meta.columns]
    df_meta = df_meta[keep_cols]

    print(f"   -> {len(df_meta)} Stationen (mit Koordinaten) geladen.")

    # 2. MESSDATEN LADEN (Temperatur & Zeit)
    all_files = glob.glob(os.path.join(INPUT_DIR, "*_*.csv"))
    print(f"📂 Gefundene Mess-Dateien: {len(all_files)}")

    dfs = []

    for f in tqdm(all_files, desc="Verarbeite Messdaten"):
        # Metadaten-Datei ignorieren, falls sie im gleichen Loop landet
        if os.path.basename(f) == METADATA_FILE:
            continue

        try:
            df = pd.read_csv(f)

            # Spaltenbereinigung: Temperatur finden
            if 'tl' in df.columns:
                df = df.rename(columns={'tl': 'temperature'})
            elif 't' in df.columns:
                df = df.rename(columns={'t': 'temperature'})

            # Station-ID bereinigen
            if 'station' in df.columns:
                if 'station_id' in df.columns:
                    df = df.drop(columns=['station_id'])
                df = df.rename(columns={'station': 'station_id'})

            # Duplikate entfernen
            df = df.loc[:, ~df.columns.duplicated()]

            # Wenn die Spalte 'temperature' oder 'time' gar nicht existiert -> Datei überspringen
            if 'temperature' not in df.columns or 'time' not in df.columns:
                continue

            #Zeilen skippen, wo Temperatur fehlt (NaN/None)
            initial_count = len(df)
            df = df.dropna(subset=['temperature'])

            # Falls durch das Löschen die Datei leer wurde -> weitermachen
            if df.empty:
                continue

            # Nur relevante Spalten behalten
            df = df[['time', 'station_id', 'temperature']]

            dfs.append(df)

        except Exception as e:
            print(f"Fehler bei Datei {os.path.basename(f)}: {e}")

    if not dfs:
        print("Keine gültigen Messdaten gefunden!")
        return

    # 3. ZUSAMMENFÜGEN & MERGEN
    print("Füge alle Messdaten zusammen...")
    master_df = pd.concat(dfs, ignore_index=True)

    # Check auf Duplikate im Master
    master_df = master_df.loc[:, ~master_df.columns.duplicated()]

    print("Verbinde Messdaten mit Koordinaten...")
    # 'inner' join: Behalte nur Daten, wo wir AUCH Koordinaten haben
    final_df = pd.merge(master_df, df_meta, on='station_id', how='inner')

    # 4. FEATURE ENGINEERING
    print("Generiere Zeit-Features (hour, month, weekday...)...")

    # Zeit parsen
    final_df['time'] = pd.to_datetime(final_df['time'], utc=True)

    # Die angeforderten Features extrahieren
    final_df['hour'] = final_df['time'].dt.hour
    final_df['month'] = final_df['time'].dt.month
    final_df['dayofyear'] = final_df['time'].dt.dayofyear
    final_df['weekday'] = final_df['time'].dt.weekday  # 0 = Montag

    # 5. FINALISIEREN & SPEICHERN
    # Zur Sicherheit am Ende nochmal leere Zeilen löschen (wo Temp oder Koordinaten fehlen)
    req_cols = ['temperature', 'latitude', 'longitude', 'elevation']
    final_df = final_df.dropna(subset=req_cols)

    # Sortieren
    final_df = final_df.sort_values(by=['time', 'station_id'])

    print(f"Fertig! {len(final_df)} Zeilen bereit.")
    print("Enthaltene Spalten:", list(final_df.columns))

    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved unter: {os.path.abspath(OUTPUT_FILE)}")


if __name__ == "__main__":
    create_master_dataset()