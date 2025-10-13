import argparse
import pathlib
import requests
import sys

def test_minio_upload(base_url: str, file_path: pathlib.Path) -> None:
    if not file_path.exists():
        print(f"file not found: {file_path}")
        sys.exit(1)

    try:
        print(f"starting upload to url:  {base_url}")
        print(f"File: {file_path} ({file_path.stat().st_size} Bytes)")

        with file_path.open("rb") as f:
            resp = requests.post(
                f"{base_url}/api/storage/upload",
                files={"file": (file_path.name, f, "image/jpeg")},
                timeout=30,
            )

        if resp.status_code == 200:
            data = resp.json()
            print(f"Upload succeded:")
            print(f"Bucket: {data.get('bucket')}")
            print(f"Object: {data.get('object')}")
            print(f"Content-Type: {data.get('content_type')}")
        else:
            print(f"Upload failed ({resp.status_code}): {resp.text}")
            sys.exit(2)

    except Exception as e:
        print(f"Upload-test failed: {e}")
        sys.exit(3)

if __name__ == "__main__":
    script_dir = pathlib.Path(__file__).resolve().parent
    default_test_file = (script_dir.parent / "testdata" / "miniotest.jpg").resolve()

    ap = argparse.ArgumentParser(description="MinIO Upload-Test")
    ap.add_argument("--base", default="http://127.0.0.1:8000", help="API-Base-URL")
    ap.add_argument("--file", default=str(default_test_file), help="Path to fIle (.jpg)")
    args = ap.parse_args()

    test_minio_upload(args.base, pathlib.Path(args.file))
