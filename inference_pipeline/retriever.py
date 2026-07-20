"""
Retriever: runs filtered vector search across expanded queries and
merges/deduplicates the results.
"""
from qdrant_client.http.models import FieldCondition, Filter, MatchValue

from feature_pipeline.embedding import get_model
from feature_pipeline.vector_db import COLLECTION_NAME, get_client
from inference_pipeline.query_expansion import expand_query
from inference_pipeline.self_query import extract_filters


def _build_filter(filters: dict) -> Filter | None:
    if filters.get("source"):
        return Filter(must=[FieldCondition(key="source", match=MatchValue(value=filters["source"]))])
    return None


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """Expand the query, embed each variant, and search Qdrant with filters."""
    client = get_client()
    embed_model = get_model()

    filters = extract_filters(query)
    qdrant_filter = _build_filter(filters)

    variants = expand_query(query)
    seen_ids = set()
    results = []

    for variant in variants:
        vector = embed_model.encode(variant).tolist()
        hits = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            query_filter=qdrant_filter,
            limit=top_k,
        )
        for hit in hits:
            if hit.id not in seen_ids:
                seen_ids.add(hit.id)
                results.append({"score": hit.score, **hit.payload})

    return results
