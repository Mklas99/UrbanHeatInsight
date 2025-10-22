import urllib3
from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.core.logger_config import logger


class MinioClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        """Get or create a MinioClient instance"""
        if cls._instance is None:
            cls._instance = MinioClient()
        return cls._instance

    def __init__(self):
        self.client = self._create_client()

    def _create_client(self) -> Minio:
        # Needed cause minio wants a host without http(s) and the information separated
        ep = settings.minio_endpoint_effective
        secure = ep.startswith("https://")
        host = ep.removeprefix("http://").removeprefix("https://")

        try:
            http_client = urllib3.PoolManager(
                timeout=urllib3.Timeout(connect=2.0, read=8.0),
                retries=False,
            )
            minio_client = Minio(
                host,
                access_key=settings.MINIO_ROOT_USER,
                secret_key=settings.MINIO_ROOT_PASSWORD,
                secure=secure,
                http_client=http_client,
            )
            logger.info(f"Minio endpoint in use: {ep}")
            return minio_client
        except Exception as e:
            logger.error(f"Minio client creation failed: {e}")
            raise

    def ensure_bucket_exists(self, bucket: str) -> Minio:
        """
        Bucket Check -> Else generate bucket
        """
        try:
            self.get_instance().client.list_buckets()

            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                logger.info(f"Minio Bucket '{bucket}' created.")
            else:
                logger.info(f"Minio Bucket '{bucket}' is available.")
        except S3Error as e:
            logger.error(f"Minio, failed existing check: {e}")
            raise

        return self.client
