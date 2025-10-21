import sys

import requests


def test_minio_delete(base_url: str, object_name: str) -> None:
    try:
        resp = requests.delete(f"{base_url}/api/storage/delete/{object_name}", timeout=20)
        if resp.status_code == 200:
            print(f"Deleted: {resp.json()}")
        else:
            print(f"Error on delete ({resp.status_code}): {resp.text}")
            sys.exit(2)
    except Exception as e:
        print(f"Delete failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    url = "http://127.0.0.1:8000"
    object = "miniotest.jpg"
    test_minio_delete(url, object)
