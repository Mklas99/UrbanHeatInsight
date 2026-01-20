import os
import pandas as pd
import numpy as np
from PIL import Image

BASE_DIR = "../data_old"
STATION_DIR = os.path.join(BASE_DIR, "stations")
IMG_DIR = os.path.join(BASE_DIR, "images")

os.makedirs(STATION_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

print(f"Erstelle Daten in: {os.path.abspath(BASE_DIR)}")

stations = [
    {"id": "wien_city", "elev": 170, "color": (100, 100, 100)},
    {"id": "salzburg_airport", "elev": 430, "color": (50, 200, 50)},
    {"id": "gundeck_alpe", "elev": 1200, "color": (20, 100, 20)},
    {"id": "sonnblick", "elev": 3100, "color": (250, 250, 250)},
    {"id": "zell_am_see", "elev": 750, "color": (0, 0, 200)}
]

dates = pd.date_range(start="2023-06-01", periods=72, freq="H")

for s in stations:
    sid = s["id"]
    elev = s["elev"]

    img = Image.new('RGB', (224, 224), color=s["color"])

    pixels = np.array(img)
    noise = np.random.randint(-20, 20, pixels.shape)
    pixels = np.clip(pixels + noise, 0, 255).astype('uint8')
    img_noisy = Image.fromarray(pixels)

    img_path = os.path.join(IMG_DIR, f"{sid}.png")
    img_noisy.save(img_path)
    print(f"Bild erstellt: {img_path}")

    base_temp = 25.0
    lapse_rate = 0.0065 * elev

    temps = []
    for date in dates:
        hour = date.hour
        day_cycle = 5.0 * np.sin((hour - 8) * np.pi / 12)

        noise = np.random.normal(0, 0.5)

        t = base_temp - lapse_rate + day_cycle + noise
        temps.append(t)

    df = pd.DataFrame({
        'time': dates,
        'temperature': temps,
        'elevation': [elev] * len(dates)
    })

    csv_path = os.path.join(STATION_DIR, f"{sid}.csv")
    df.to_csv(csv_path, index=False)
    print(f"Data created: {csv_path}")