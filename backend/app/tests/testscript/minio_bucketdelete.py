from minio import Minio
from minio.deleteobjects import DeleteObject
import sys


def delete_bucket(endpoint, access_key, secret_key, bucket_name, secure=False):
    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
    # Prüfen, ob Bucket existiert
    if not client.bucket_exists(bucket_name):
        print(f"[!] Bucket '{bucket_name}' existiert nicht.")
        return
    print(f"[i] Lösche alle Objekte aus Bucket '{bucket_name}' ...")
    # Alle Objekte auflisten und löschen
    objects = client.list_objects(bucket_name, recursive=True)
    delete_objects = (DeleteObject(obj.object_name) for obj in objects)
    for error in client.remove_objects(bucket_name, delete_objects):
        print(f"[!] Fehler beim Löschen von {error.object_name}: {error}")

    # Bucket löschen
    client.remove_bucket(bucket_name)
    print(f"[✓] Bucket '{bucket_name}' wurde vollständig gelöscht.")


def main():
    endpoint = "localhost:9000"   # oder "localhost:9001"
    access_key = "minioadmin"
    secret_key = "minioadmin123"
    bucket_name = "uhiprocessed"   # <--- Deinen Bucket-Namen hier eintragen
    secure = False                # True, falls HTTPS aktiv ist

    try:
        delete_bucket(endpoint, access_key, secret_key, bucket_name, secure)
    except Exception as e:
        print(f"[!] Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
