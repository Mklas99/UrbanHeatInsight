import os
import re
import logging
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError, DBAPIError

from backend.app.core.config import settings

# Load sensitive data from environment variables
DATABASE_URL = settings.db_url  # <-- use the instance property

def validate_database_url(url: str):
    # Basic validation for asyncpg PostgreSQL URL
    pattern = r"^postgresql\+asyncpg:\/\/[^:]+:[^@]+@[^:]+:\d+\/.+$"
    if not url or not re.match(pattern, url):
        logging.error("Invalid or missing DATABASE_URL environment variable.")
        raise ValueError("DATABASE_URL is misconfigured. Check your environment variables.")

validate_database_url(DATABASE_URL)

# Connection pool settings for better performance
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_size=10,           # Number of connections to keep in the pool
    max_overflow=20,        # Maximum number of connections to go beyond pool_size
    pool_timeout=30,        # Timeout in seconds for getting a connection from the pool
)

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db_session(retries: int = 3, backoff: float = 0.5) -> AsyncSession:
    """
    Get a database session with retry logic for transient errors.
    """
    attempt = 0
    while attempt < retries:
        try:
            async with AsyncSessionLocal() as session:
                yield session
            break
        except (OperationalError, DBAPIError) as e:
            logging.warning(f"Transient DB error: {e}. Retrying ({attempt+1}/{retries})...")
            attempt += 1
            await asyncio.sleep(backoff * (2 ** attempt))
        except Exception as e:
            logging.error(f"Error in database session: {e}")
            raise
    else:
        logging.error("Exceeded maximum DB connection retries.")
        raise RuntimeError("Could not connect to the database after several retries.")

# NOTE: For production, use Alembic for migrations instead of Base.metadata.create_all.
# Alembic allows for safe, versioned schema
