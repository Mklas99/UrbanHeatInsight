from pydantic import PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BACKEND_PORT: PositiveInt = 8000
    LOG_LEVEL: str = "info"

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "uhidb"
    POSTGRES_PORT: PositiveInt = 5432
    POSTGRES_HOST: str = "localhost"

    PGADMIN_PORT: PositiveInt = 5050
    PGADMIN_DEFAULT_EMAIL: str = "admin@example.com"
    PGADMIN_DEFAULT_PASSWORD: str = "admin123"

    MLFLOW_PORT: PositiveInt = 5000

    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin123"
    MINIO_BUCKET_RAW: str = "uhi-raw"
    MINIO_BUCKET_PROCESSED: str = "uhi-processed"
    MINIO_PORT: PositiveInt = 9000
    MINIO_CONSOLE_PORT: PositiveInt = 9001
    MINIO_ENDPOINT: str | None = None
    ENV: str = "dev"   # "docker" oder "dev"

    DATABASE_URL: str | None = None
    @property
    def db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @property
    def minio_endpoint_effective(self) -> str:
        # ENV überschreibt Default-Host
        if self.MINIO_ENDPOINT and self.MINIO_ENDPOINT.strip():
            return self.MINIO_ENDPOINT.strip()
        if self.ENV.lower() == "docker":
            return f"http://minio:{self.MINIO_PORT}"
        return f"http://127.0.0.1:{self.MINIO_PORT}"

settings = Settings()
