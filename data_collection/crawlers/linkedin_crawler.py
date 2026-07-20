"""
Crawler for your own LinkedIn posts/articles.

LinkedIn has no public scraping API for personal posts, so the book's
approach (and the recommended one here) is to use your LinkedIn data
export (Settings -> "Get a copy of your data") rather than scraping.

This module reads that exported archive and normalizes it into the
common raw-document schema.
"""
import csv
from datetime import datetime, timezone
from pathlib import Path


def load_linkedin_export(export_dir: str, author: str) -> list[dict]:
    """
    Parse a LinkedIn data export directory into raw documents.

    Expects a `Shares.csv` (or similar) file inside `export_dir`,
    as produced by LinkedIn's "Get a copy of your data" export.

    TODO: adjust column names to match the exact export format
    LinkedIn gives you (these change over time).
    """
    docs = []
    shares_path = Path(export_dir) / "Shares.csv"
    if not shares_path.exists():
        raise FileNotFoundError(
            f"Expected a LinkedIn export at {shares_path}. "
            "Download it from LinkedIn Settings > Get a copy of your data."
        )

    with open(shares_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            docs.append(
                {
                    "source": "linkedin",
                    "author": author,
                    "url": row.get("ShareLink", ""),
                    "date": row.get("Date", datetime.now(timezone.utc).isoformat()),
                    "raw_text": row.get("ShareCommentary", ""),
                    "title": "",
                }
            )
    return docs


if __name__ == "__main__":
    results = load_linkedin_export("./linkedin_export", author="me")
    print(f"Loaded {len(results)} LinkedIn posts")
