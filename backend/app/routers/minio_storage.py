import io
import socket
from datetime import timedelta

import anyio
from fastapi import APIRouter, HTTPException, UploadFile, status
from minio.error import S3Error

from app.core.config import settings
from app.core.logger_config import logger
from app.services.minio_client import get_minio_client

router = APIRouter(prefix="/storage", tags=["storage"])

# ping / list / upload / presigned-url / delete


# Check Minio connection and bucket existence (used for debugging TODO: remove in production ?)
@router.get("/ping")
def minio_ping():
    # Needed cause minio wants a host without http(s) and the information separated
    ep = settings.minio_endpoint_effective
    secure = ep.startswith("https://")
    hostport = ep.removeprefix("http://").removeprefix("https://")
    host, _, port = hostport.partition(":")
    port = int(port or (443 if secure else 80))
    try:
        logger.info(f"Minio ping {host}:{port}")
        with socket.create_connection((host, port), timeout=3) as s:
            pass

        client = get_minio_client()
        buckets = [b.name for b in client.list_buckets()]
        return {
            "ok": True,
            "endpoint": ep,
            "buckets": buckets,
        }
    except OSError as e:
        logger.error(f"minio socket error: {e}")
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
        logger.exception("minio ping failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/upload")
async def upload_file(file: UploadFile):
    client = get_minio_client()
    bucket = settings.MINIO_BUCKET_RAW
    try:
        # read data length -> minio needs it otherwhise timeouts (even on small files)
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Empty file or no file")
        object_name = file.filename
        content_type = file.content_type or "application/octet-stream"

        def _put():
            return client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )

        # TODO: Check if working with Multifile
        # use background thread cause synchron stream while asynchron architecture
        res = await anyio.to_thread.run_sync(_put)
        # verify upload with previous mechanic
        stat = await anyio.to_thread.run_sync(lambda: client.stat_object(bucket, object_name))

        logger.info(f"Upload verficated: {bucket}/{object_name} size={stat.size}")
        return {
            "ok": True,
            "bucket": bucket,
            "object": res.object_name,
            "size": stat.size,
            "etag": getattr(res, "etag", None),
            "content_type": content_type,
        }

    except S3Error as e:
        logger.error(f"MinIO S3Error: {e}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Minio error: {e.code}")
    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")
    finally:
        try:
            await file.close()
        except Exception:
            pass


# download
@router.get("/presigned/{object_name:path}")
def get_presigned_url(object_name: str, expires_seconds: int = 600):
    """
    getting temporary presigned url for downloading an object
    """
    client = get_minio_client()
    bucket = settings.MINIO_BUCKET_RAW
    try:
        url = client.presigned_get_object(
            bucket_name=bucket,
            object_name=object_name,
            expires=timedelta(seconds=expires_seconds),
        )
        logger.info(f"created presigned url: {object_name}")
        return {"ok": True, "url": url, "expires_in": expires_seconds}
    except S3Error as e:
        logger.error(f"Minio S3Error for presigned url: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Object not found / no permission: {e.code}",
        ) from e
    except Exception as e:
        logger.exception("Failed to get presigned url")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get presigned url: {e}",
        ) from e


@router.get("/list")
def list_objects(prefix: str = ""):
    client = get_minio_client()
    bucket = settings.MINIO_BUCKET_RAW
    objs = client.list_objects(bucket, prefix=prefix, recursive=True)
    return {"bucket": bucket, "objects": [o.object_name for o in objs]}


@router.delete("/delete/{object_name:path}")
def delete_object(object_name: str):
    client = get_minio_client()
    bucket = settings.MINIO_BUCKET_RAW
    try:
        client.remove_object(bucket_name=bucket, object_name=object_name)
        logger.info(f"Object deleted: {bucket}/{object_name}")
        return {"ok": True, "deleted": object_name, "bucket": bucket}

    except S3Error as e:
        logger.error(f"minio S3Error while deleting: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Objekt nicht gefunden oder Zugriff verweigert: {e.code}",
        ) from e
    except Exception as e:
        logger.exception("Error while deleting object")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deleting failed: {e}",
        ) from e
