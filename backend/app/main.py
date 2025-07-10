from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="UrbanHeatmap API")

# Setup structured logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "req"):
            log_record["req"] = record.req
        if hasattr(record, "res"):
            log_record["res"] = record.res
        return json.dumps(log_record)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.root.handlers = [handler]
logging.root.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        logger.info("request", extra={
            "req": {"method": request.method, "url": str(request.url)},
            "res": {"status_code": response.status_code}
        })
        return response

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
