from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.logger_config import logger, LogMiddleware
from .database.database import engine, Base
from .routers import heatmap, collector_router

app = FastAPI(
    title="UrbanHeatmap API",
    description="API for urban heat mapping and data collection",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LogMiddleware)

app.include_router(heatmap.router, prefix="/api", tags=["heatmap"])
app.include_router(collector_router.router, prefix="/api", tags=["collector"])

@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database tables on startup."""
    try:
        logger.info("Starting UrbanHeatmap API...")
    except Exception as exc:
        logger.error(f"Startup error: {exc}")
        raise

@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    try:
        logger.info("Shutting down UrbanHeatmap API...")
        await engine.dispose()
    except Exception as exc:
        logger.error(f"Shutdown error: {exc}")

@app.get("/", response_model=dict)
async def root() -> dict:
    """Health check endpoint."""
    return {"message": "UrbanHeatmap API is running", "status": "healthy"}

@app.get("/health", response_model=dict)
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
    return error_response(
        "validation_error",
        "Validation failed",
        exc.errors()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    logger.error(f"Unhandled error: {exc}")
    return error_response(
        "internal_server_error",
        "An unexpected error occurred.",
        str(exc)
    )
