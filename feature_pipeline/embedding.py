"""
Embedding: turns text chunks into vectors using a sentence-transformer
model.
"""
import os

from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        model_name = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
        _model = SentenceTransformer(model_name)
    return _model


def embed_chunks(chunk_records: list[dict]) -> list[dict]:
    """Attach an `embedding` vector to each chunk record."""
    model = get_model()
    texts = [c["text"] for c in chunk_records]
    vectors = model.encode(texts, show_progress_bar=True)
    for record, vector in zip(chunk_records, vectors):
        record["embedding"] = vector.tolist()
    return chunk_records
