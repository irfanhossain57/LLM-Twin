"""
Monitoring: logs live queries/outputs from the inference service for
drift and quality tracking over time.

This is a minimal local-file logger. Swap in a real observability
tool (e.g. Opik, as the book uses) as a drop-in replacement -- keep
the same `log_interaction` signature.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path("evaluation/monitoring/interaction_log.jsonl")


def log_interaction(query: str, output: str, retrieved_chunk_ids: list[str]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "output": output,
        "retrieved_chunk_ids": retrieved_chunk_ids,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
