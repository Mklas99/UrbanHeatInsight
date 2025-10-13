import pathlib
import requests
import sys

def test_minio_download(base_url: str, object_name: str, out_path: pathlib.Path | None):
    try:
        # getting presigned url
        r = requests.get(f"{base_url}/api/storage/presigned/{object_name}",
                         params={"expires_seconds": 600}, timeout=15)
        r.raise_for_status()
        url = r.json()["url"]

        # download
        resp = requests.get(url, stream=True, timeout=30)
        resp.raise_for_status()

        # destination path
        if out_path is None:
            out_path = pathlib.Path(object_name).name
            out_path = pathlib.Path.cwd() / out_path
        else:
            out_path = pathlib.Path(out_path)
            if out_path.is_dir():
                out_path = out_path / pathlib.Path(object_name).name
            out_path.parent.mkdir(parents=True, exist_ok=True)

        # saving
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"Download succeded {out_path} ({out_path.stat().st_size} Bytes)")
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(2)

if __name__ == "__main__":
    base = "http://127.0.0.1:8000"
    object_name = "miniotest.jpg"

    # destination: app/tests/download_[object] (like the upload test)
    script_dir = pathlib.Path(__file__).resolve().parent
    tests_dir = script_dir.parent / "testdata"
    tests_dir.mkdir(exist_ok=True)
    out_path = tests_dir / f"download_{object_name}"

    try:
        test_minio_download(base, object_name, out_path)
    except requests.HTTPError as e:
        resp = e.response
        print(f"HTTP {resp.status_code} from API: {resp.text}")
        raise