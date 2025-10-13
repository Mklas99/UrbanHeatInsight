from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from app.core.logger_config import logger
import urllib3


def get_minio_client() -> Minio:
    # Needed cause minio wants a host without http(s) and the information separated
    ep = settings.minio_endpoint_effective
    secure = ep.startswith("https://")
    host = ep.removeprefix("http://").removeprefix("https://")
    logger.info(f"Minio endpoint in use: {ep}")

    http_client = urllib3.PoolManager(
        timeout=urllib3.Timeout(connect=2.0, read=8.0),
        retries=False,
    )
    return Minio(
        host,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=secure,
        http_client=http_client,
    )


def ensure_bucket_exists(bucket: str) -> Minio:
    """
    Bucket Check -> Else generate bucket
    """
    client = get_minio_client()
    try:
        client.list_buckets()

        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            logger.info(f"Minio Bucket '{bucket}' created.")
        else:
            logger.info(f"Minio Bucket '{bucket}' is available.")
    except S3Error as e:
        logger.error(f"Minio, failed existing check: {e}")
        raise

    return client