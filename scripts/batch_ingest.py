"""Batch ingest all documents from the full dataset into the running backend."""
import sys, os, time, hashlib, requests, json
from pathlib import Path

API = "http://127.0.0.1:8000"
DATASET_DIR = Path(r"D:\Kunpeng\赛题5 PPT文档结构化检索与问答_完整集\dataset\documents")

def get_existing_hashes():
    """Get set of file hashes already in catalog."""
    try:
        resp = requests.get(f"{API}/docs", timeout=10)
        docs = resp.json()
        return {d.get("file_hash", "") for d in docs}
    except Exception as e:
        print(f"Failed to get catalog: {e}")
        return set()

def upload_file(filepath):
    """Upload a single file, return doc_id or None."""
    try:
        with open(filepath, "rb") as f:
            resp = requests.post(f"{API}/ingest", files={"file": (filepath.name, f)})
        if resp.status_code == 200:
            data = resp.json()
            return data.get("docId")
        else:
            print(f"  Upload failed: {resp.status_code} {resp.text[:100]}")
            return None
    except Exception as e:
        print(f"  Upload error: {e}")
        return None

def hash_file(filepath):
    """Compute SHA256 prefix matching the backend's _sha256_prefix."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:32]

def main():
    # Find all supported files
    files = sorted([f for f in DATASET_DIR.iterdir() if f.suffix.lower() in {".ppt", ".pptx", ".pdf"}])
    print(f"Found {len(files)} documents in dataset")

    # Get existing hashes to skip duplicates
    existing_hashes = get_existing_hashes()
    print(f"Already indexed: {len(existing_hashes)}")

    to_upload = []
    for fp in files:
        fhash = hash_file(fp)
        if fhash not in existing_hashes:
            to_upload.append(fp)
        else:
            print(f"  SKIP (exists): {fp.name}")

    print(f"\nUploading {len(to_upload)} new documents...\n")

    for i, fp in enumerate(to_upload):
        print(f"[{i+1}/{len(to_upload)}] {fp.name} ({fp.suffix}) ... ", end="", flush=True)
        doc_id = upload_file(fp)
        if doc_id:
            print(f"OK ({doc_id})")
        else:
            print("FAILED")
        time.sleep(0.3)  # Small delay between uploads

    # Wait for all to finish indexing
    print("\nWaiting for all documents to finish indexing...")
    deadline = time.time() + 1800  # 30 min timeout
    while time.time() < deadline:
        try:
            resp = requests.get(f"{API}/docs", timeout=10)
            docs = resp.json()
            statuses = {}
            for d in docs:
                s = d.get("status", "pending")
                statuses[s] = statuses.get(s, 0) + 1
            print(f"  Status: {statuses}")
            if statuses.get("pending", 0) == 0 and statuses.get("parsing", 0) == 0:
                print(f"\nAll {len(docs)} documents indexed!")
                return
        except Exception as e:
            print(f"  Poll error: {e}")
        time.sleep(10)

    print("\nTimeout! Not all documents finished.")

if __name__ == "__main__":
    main()
