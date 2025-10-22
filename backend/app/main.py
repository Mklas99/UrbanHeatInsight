import os
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# uvicorn requires the app to be importable, so we adjust sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.clients.minio_client import MinioClient
from app.core.config import settings
from app.core.logger_config import LogMiddleware, logger, setup_logging
from app.database.database import engine
from app.routers.minio_storage_api import router as MinioStorageApi
from app.routers.system_api import router as SystemApiRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    Ensures proper initialization and cleanup of resources.
    """
    try:
        """Initialize database tables on startup."""
        setup_logging(settings)
        MinioClient.get_instance().ensure_bucket_exists(settings.MINIO_BUCKET_RAW)
        MinioClient.get_instance().ensure_bucket_exists(settings.MINIO_BUCKET_PROCESSED)
        logger.info("Starting UrbanHeatmap API...")
        yield
    except Exception as exc:
        logger.error(f"Startup error: {exc}")
        raise
    finally:
        """Cleanup on shutdown."""
        try:
            logger.info("Shutting down UrbanHeatmap API...")
            await engine.dispose()
        except Exception as exc:
            logger.error(f"Shutdown error: {exc}")


app = FastAPI(
    title="UrbanHeatmap API",
    description="API for urban heat mapping and data collection",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LogMiddleware)

app.include_router(MinioStorageApi, prefix="/api/storage", tags=["minio"])
app.include_router(SystemApiRouter, prefix="/system", tags=["system"])


########## Exception Handlers ##########
def error_response(error_type: str, message: str, details: object = None) -> JSONResponse:
    """Format error responses."""
    logger.error(f"Error occurred: {error_type}, {message}, {details}")
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
        logger.warning(f"404 Not Found: {request.url.path}")
        return error_response("not_found", "Resource not found", {"path": request.url.path})
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"type": "http_error", "message": exc.detail}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors."""
    logger.error(f"Validation error: {exc}")
    return error_response("validation_error", "Validation failed", exc.errors())


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    logger.error(f"Unhandled error: {exc}")
    return error_response("internal_server_error", "An unexpected error occurred.", str(exc))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
