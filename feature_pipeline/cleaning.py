"""
Cleaning: strips markup/boilerplate and normalizes raw text before
chunking.
"""
import re


def clean_text(raw_text: str) -> str:
    """Normalize whitespace, strip stray markup, drop empty lines."""
    text = re.sub(r"<[^>]+>", " ", raw_text)          # strip any leftover HTML tags
    text = re.sub(r"http\S+", "", text)                  # strip bare URLs
    text = re.sub(r"[ \t]+", " ", text)                   # collapse whitespace
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def clean_documents(docs: list[dict]) -> list[dict]:
    """Apply clean_text to a batch of raw documents, in place of raw_text."""
    cleaned = []
    for doc in docs:
        doc = dict(doc)
        doc["clean_text"] = clean_text(doc.get("raw_text", ""))
        cleaned.append(doc)
    return cleaned
