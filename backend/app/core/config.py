import logging
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "urbanheatmap")
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    @property
    def db_url(self):
        if self.DATABASE_URL:
            logging.info("Using DATABASE_URL from environment variable.")
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "UrbanHeatmap API"
        
    # File uploads
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "/tmp/uploads"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # <-- Add this line to ignore extra env vars

settings = Settings()
# Ensure DATABASE_URL is always set for downstream code
os.environ["DATABASE_URL"] = settings.db_url
