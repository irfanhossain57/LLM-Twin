"""
Data warehouse layer: persists raw documents (from any crawler) into a
single NoSQL store, acting as the single source of truth for raw
content across the whole project.
"""
import os

from pymongo import MongoClient
from pymongo.collection import Collection


def get_collection() -> Collection:
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "llm_twin_raw")
    client = MongoClient(uri)
    return client[db_name]["raw_documents"]


def save_documents(docs: list[dict]) -> int:
    """
    Upsert raw documents by URL (dedupes re-crawls of the same content).
    Returns the number of documents written.
    """
    if not docs:
        return 0
    collection = get_collection()
    written = 0
    for doc in docs:
        result = collection.update_one(
            {"url": doc["url"]}, {"$set": doc}, upsert=True
        )
        if result.upserted_id or result.modified_count:
            written += 1
    return written


def load_all_documents(source: str | None = None) -> list[dict]:
    """Load all raw documents, optionally filtered by source."""
    collection = get_collection()
    query = {"source": source} if source else {}
    return list(collection.find(query))
