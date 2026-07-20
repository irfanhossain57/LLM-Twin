"""
Lightweight dataset versioning: snapshots the instruction dataset with
a version tag, so training runs can be tied back to the exact data
that produced them.

For a course project, local file-based versioning is enough; this is
a natural place to swap in a real dataset registry (e.g. Hugging Face
Hub datasets, DVC) later.
"""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

VERSIONS_DIR = Path("training_pipeline/dataset_versions")


def snapshot_dataset(source_path: str = "training_pipeline/instruct_dataset.jsonl") -> str:
    """Copy the current dataset into a timestamped version folder."""
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest_path = VERSIONS_DIR / f"instruct_dataset_{timestamp}.jsonl"
    shutil.copy(source_path, dest_path)

    with open(source_path, encoding="utf-8") as f:
        row_count = sum(1 for _ in f)

    manifest_path = VERSIONS_DIR / "manifest.jsonl"
    with open(manifest_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"version": timestamp, "path": str(dest_path), "rows": row_count}) + "\n")

    return timestamp


if __name__ == "__main__":
    version = snapshot_dataset()
    print(f"[dataset_versioning] snapshotted dataset as version {version}")
