import io
import socket
from datetime import timedelta

import anyio
from fastapi import HTTPException, UploadFile, status
from minio.error import S3Error

from app.clients.minio_client import MinioClient
from app.core.config import settings
from app.core.logger_config import logger
from app.models.bucket_names import MinIOBuckets


class MinioStorageService:
    def __init__(self):
        self.logger = logger.getChild("MinioStorageService")
        self.client = MinioClient.get_instance().client
        self.bucket = settings.MINIO_BUCKET_RAW

    def ping(self):
        ep = settings.minio_endpoint_effective
        secure = ep.startswith("https://")
        hostport = ep.removeprefix("http://").removeprefix("https://")
        host, _, port = hostport.partition(":")
        port = int(port or (443 if secure else 80))
        try:
            self.logger.info(f"Minio ping {host}:{port}")
            with socket.create_connection((host, port), timeout=3) as s:
                pass

            buckets = [b.name for b in self.client.list_buckets()]
            return {
                "ok": True,
                "endpoint": ep,
                "buckets": buckets,
            }
        except OSError as e:
            self.logger.error(f"minio socket error: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "step": "socket",
                    "details": {
                        "configured_endpoint": ep,
                        "host": host,
                        "port": port,
                        "secure": secure,
                        "socket_ok": False,
                        "socket_error": str(e),
                    },
                },
            )
        except Exception as e:
            self.logger.exception("minio ping failed")
            raise HTTPException(status_code=500, detail=str(e)) from e

    async def upload_file(self, file: UploadFile, bucket: str = "uhi-raw"):
        if not file:
            raise HTTPException(status_code=400, detail="File is required")

        try:
            data = await file.read()
            if not data:
                raise HTTPException(status_code=400, detail="Empty file or no file")
            object_name = file.filename
            content_type = file.content_type or "application/octet-stream"

            def _put():
                return self.client.put_object(
                    bucket_name=self.bucket,
                    object_name=object_name,
                    data=io.BytesIO(data),
                    length=len(data),
                    content_type=content_type,
                )

            # TODO: check if anyio.to_thread.run_sync is working here
            res = await anyio.to_thread.run_sync(_put)
            stat = await anyio.to_thread.run_sync(lambda: self.client.stat_object(self.bucket, object_name))

            self.logger.info(f"Upload verified: {self.bucket}/{object_name} size={stat.size}")
            return {
                "ok": True,
                "bucket": self.bucket,
                "object": res.object_name,
                "size": stat.size,
                "etag": getattr(res, "etag", None),
                "content_type": content_type,
            }

        except S3Error as e:
            self.logger.error(f"MinIO S3Error: {e}")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Minio error: {e.code}")
        except Exception as e:
            self.logger.exception("Upload failed")
            raise HTTPException(status_code=500, detail=f"Upload failed: {e}")
        finally:
            try:
                await file.close()
            except Exception:
                pass

    def get_presigned_url(self, object_name: str, expires_seconds: int = 600):
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=timedelta(seconds=expires_seconds),
            )
            self.logger.info(f"Created presigned url: {object_name}")
            return {"ok": True, "url": url, "expires_in": expires_seconds}
        except S3Error as e:
            self.logger.error(f"Minio S3Error for presigned url: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Object not found / no permission: {e.code}",
            ) from e
        except Exception as e:
            self.logger.exception("Failed to get presigned url")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get presigned url: {e}",
            ) from e

    def list_objects(self, prefix: str = ""):
        objs = self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
        return {"bucket": self.bucket, "objects": [o.object_name for o in objs]}

    def delete_object(self, object_name: str):
        try:
            self.client.remove_object(bucket_name=self.bucket, object_name=object_name)
            self.logger.info(f"Object deleted: {self.bucket}/{object_name}")
            return {"ok": True, "deleted": object_name, "bucket": self.bucket}

        except S3Error as e:
            self.logger.error(f"Minio S3Error while deleting: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object not found or access denied: {e.code}",
            ) from e
        except Exception as e:
            self.logger.exception("Error while deleting object")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Deleting failed: {e}",
            ) from e
