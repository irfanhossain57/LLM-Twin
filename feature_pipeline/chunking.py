"""
Chunking: splits cleaned documents into overlapping chunks sized for
the embedding model's context window.
"""

DEFAULT_CHUNK_SIZE = 512   # characters; tune to your embedding model
DEFAULT_OVERLAP = 64


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text] if text else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def chunk_documents(cleaned_docs: list[dict]) -> list[dict]:
    """
    Turn cleaned documents into chunk-level records, each carrying
    the parent document's metadata plus a chunk id.
    """
    chunk_records = []
    for doc in cleaned_docs:
        chunks = chunk_text(doc.get("clean_text", ""))
        for i, chunk in enumerate(chunks):
            chunk_records.append(
                {
                    "chunk_id": f"{doc['url']}::{i}",
                    "parent_url": doc["url"],
                    "source": doc["source"],
                    "author": doc["author"],
                    "date": doc["date"],
                    "text": chunk,
                }
            )
    return chunk_records
