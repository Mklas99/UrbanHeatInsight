from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .logger_config import logger, LogMiddleware

app = FastAPI(title="UrbanHeatmap API")

app.add_middleware(LogMiddleware)

@app.get("/api/heatmap")
def get_heatmap_data():
    sample = [
        {"lat": 48.2082, "lon": 16.3738, "intensity": 0.5},
        {"lat": 48.209, "lon": 16.37, "intensity": 0.8},
        {"lat": 48.207, "lon": 16.375, "intensity": 0.3},
        {"lat": 48.21, "lon": 16.38, "intensity": 0.7},
    ]
    return {"points": sample}

# Serve frontend build
app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="static")
