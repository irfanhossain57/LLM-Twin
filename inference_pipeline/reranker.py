"""
Reranker: reorders retrieved chunks against the ORIGINAL query using a
cross-encoder, since bi-encoder retrieval scores alone are a weak
relevance signal.
"""
from sentence_transformers import CrossEncoder

_reranker: CrossEncoder | None = None


def get_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker


def rerank(query: str, candidates: list[dict], top_k: int = 3) -> list[dict]:
    """Rerank candidate chunks against the query, return the top_k."""
    if not candidates:
        return []

    reranker = get_reranker()
    pairs = [(query, c["text"]) for c in candidates]
    scores = reranker.predict(pairs)

    for candidate, score in zip(candidates, scores):
        candidate["rerank_score"] = float(score)

    return sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)[:top_k]
