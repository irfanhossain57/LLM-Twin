"""
Change data capture: pulls new/changed raw documents from the warehouse
and runs them through cleaning -> chunking -> embedding -> vector DB.
This is the feature pipeline entry point -- `make features` runs this.

For a course-project scale, this polls the warehouse rather than using
a true CDC stream (e.g. Mongo change streams / a message queue), which
is the book's production-grade approach and a natural extension here.
"""
from data_collection.data_warehouse import load_all_documents
from feature_pipeline.chunking import chunk_documents
from feature_pipeline.cleaning import clean_documents
from feature_pipeline.embedding import embed_chunks
from feature_pipeline.vector_db import upsert_chunks


def run() -> None:
    raw_docs = load_all_documents()
    print(f"[feature_pipeline] loaded {len(raw_docs)} raw documents")

    cleaned = clean_documents(raw_docs)
    chunks = chunk_documents(cleaned)
    print(f"[feature_pipeline] produced {len(chunks)} chunks")

    embedded = embed_chunks(chunks)
    written = upsert_chunks(embedded)
    print(f"[feature_pipeline] wrote {written} vectors to Qdrant")


if __name__ == "__main__":
    run()
