"""
Vector DB layer: upserts embedded chunks into Qdrant with metadata
for later filtered search.
"""
import os

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "llm_twin_chunks")


def get_client() -> QdrantClient:
    url = os.getenv("QDRANT_URL", "http://localhost:6333")
    return QdrantClient(url=url)


def ensure_collection(client: QdrantClient, vector_size: int) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


def upsert_chunks(chunk_records: list[dict]) -> int:
    """Upsert embedded chunk records into Qdrant. Returns count written."""
    if not chunk_records:
        return 0

    client = get_client()
    vector_size = len(chunk_records[0]["embedding"])
    ensure_collection(client, vector_size)

    points = [
        PointStruct(
            id=abs(hash(c["chunk_id"])) % (10**12),
            vector=c["embedding"],
            payload={
                "chunk_id": c["chunk_id"],
                "parent_url": c["parent_url"],
                "source": c["source"],
                "author": c["author"],
                "date": c["date"],
                "text": c["text"],
            },
        )
        for c in chunk_records
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points)
