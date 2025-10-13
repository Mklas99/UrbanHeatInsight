from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os, sys
import uvicorn
# uvicorn requires the app to be importable, so we adjust sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.logger_config import logger, LogMiddleware
from app.database.database import engine
from app.routers import heatmap, collector_router, minio_storage
from app.services.minio_client import ensure_bucket_exists
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting UrbanHeatmap API...")
    try:
        ensure_bucket_exists(settings.MINIO_BUCKET_RAW)
        ensure_bucket_exists(settings.MINIO_BUCKET_PROCESSED)
        yield
    finally:
        logger.info("Shutting down UrbanHeatmap API...")
        await engine.dispose()
app = FastAPI(
    title="UrbanHeatmap API",
    description="API for urban heat mapping and data collection",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #TODO Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LogMiddleware)
app.include_router(heatmap.router, prefix="/api", tags=["heatmap"])
app.include_router(collector_router.router, prefix="/api", tags=["collector"])
app.include_router(minio_storage.router, prefix="/api", tags=["minio"])

@app.get("/", response_model=dict)
async def health_check() -> dict:
    """Detailed health check."""
    return {"status": "healthy", "service": "UrbanHeatmap API"}

def error_response(error_type: str, message: str, details: object = None) -> JSONResponse:
    """Format error responses."""
    return JSONResponse(
        status_code=422 if error_type == "validation_error" else 404 if error_type == "not_found" else 500,
        content={
            "error": {
                "type": error_type,
                "message": message,
                "details": details,
            }
        },
    )

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    if exc.status_code == 404:
        return error_response("not_found", "Resource not found", {"path": request.url.path})
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"type": "http_error", "message": exc.detail}},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors."""
    return error_response("validation_error", "Validation failed", exc.errors())

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    logger.error(f"Unhandled error: {exc}")
    return error_response("internal_server_error", "An unexpected error occurred.", str(exc))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

