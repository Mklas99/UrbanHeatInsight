from fastapi import APIRouter, UploadFile

from app.core.logger_config import logger
from app.services.minio_storage_service import MinioStorageService

router = APIRouter()
minio_service = MinioStorageService()
# ping / list / upload / presigned-url / delete


# Check Minio connection and bucket existence (used for debugging TODO: remove in production ?)
@router.get("/ping")
def minio_ping():
    logger.info("Pinging Minio storage...")
    return minio_service.ping()


from fastapi import File

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Uploading file: {file.filename}")
    return await minio_service.upload_file(file)


# download
@router.get("/presigned/{object_name:path}")
def get_presigned_url(object_name: str, expires_seconds: int = 600):
    logger.info(f"Generating presigned URL for object: {object_name}")
    return minio_service.get_presigned_url(object_name, expires_seconds)


@router.get("/list")
def list_objects(prefix: str = ""):
    logger.info(f"Listing objects with prefix: {prefix}")
    return minio_service.list_objects(prefix)


@router.delete("/delete/{object_name:path}")
def delete_object(object_name: str):
    logger.info(f"Deleting object: {object_name}")
    return minio_service.delete_object(object_name)
