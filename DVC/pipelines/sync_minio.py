import sys
from pathlib import Path

# Backend-Modulpfad für Imports ergänzen
sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))

from app.clients.minio_client import MinioClient
from app.core.config import settings


def upload_processed(version: str = "dev") -> None:
    """
    Lädt verarbeitete GeoJSON-Dateien aus DVC/data/processed
    in den MINIO_BUCKET_PROCESSED hoch.
    """
    src_dir = Path(__file__).resolve().parents[1] / "data" / "processed"
    if not src_dir.exists():
        raise RuntimeError(f"Verzeichnis {src_dir} existiert nicht. Pipeline muss zuerst ausgeführt werden.")

    minio_client = MinioClient.get_instance().ensure_bucket_exists(settings.MINIO_BUCKET_PROCESSED)

    for path in src_dir.glob("*.geojson"):
        object_name = f"{version}/{path.name}"
        minio_client.fput_object(
            bucket_name=settings.MINIO_BUCKET_PROCESSED,
            object_name=object_name,
            file_path=str(path),
            content_type="application/geo+json",
        )

    #Test weil jpg
    for path in src_dir.glob("*.jpg"):
        object_name = f"{version}/{path.name}"
        minio_client.fput_object(
            bucket_name=settings.MINIO_BUCKET_PROCESSED,
            object_name=object_name,
            file_path=str(path),
            content_type="image/jpeg",
        )


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "dev"
    upload_processed(version)
