import logging
import os
import sys
import time
from datetime import datetime
from venv import logger

from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import Settings


def setup_logging(settings: Settings):
    """
    Configures global logging for the application.
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
        logger.info("Created logs directory.")

    # Generate log file name with current date
    log_filename = datetime.now().strftime("logs/UHI-BE_%Y-%m-%d_%H.log")

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # todo: adjust log level based on settings
    log_level = logging.DEBUG if settings.app_env == "development" else logging.DEBUG
    logging.basicConfig(
        level=log_level,  # Set the log level globally
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),  # Log to console
            logging.FileHandler(log_filename),
        ],
    )
    logging.getLogger("uvicorn").setLevel(logging.INFO)  # Adjust uvicorn log level
    logging.info(f"Logging is configured globally at {log_level} level.")


class LogMiddleware(BaseHTTPMiddleware):
    logger = logging.getLogger("LogMiddleware")

    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            "request handled",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000),
            },
        )
        return response
