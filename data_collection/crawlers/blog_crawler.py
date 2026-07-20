"""
Crawler for personal blog / Medium articles.

Turns a blog post URL into a raw document matching the common schema
used across all crawlers:

    {
        "source": "blog",
        "author": str,
        "url": str,
        "date": str (ISO 8601),
        "raw_text": str,
        "title": str,
    }
"""
from datetime import datetime, timezone
from typing import Iterable

import requests
from bs4 import BeautifulSoup


def fetch_post(url: str) -> str:
    """Fetch raw HTML for a single blog post URL."""
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.text


def extract_text(html: str) -> tuple[str, str]:
    """
    Extract (title, body_text) from a blog post's HTML.

    TODO: adjust selectors to match your blogging platform
    (Medium, Substack, Hashnode, a custom static site, etc.).
    """
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else ""
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    body_text = "\n".join(paragraphs)
    return title, body_text


def crawl(urls: Iterable[str], author: str) -> list[dict]:
    """Crawl a list of blog post URLs into raw documents."""
    docs = []
    for url in urls:
        html = fetch_post(url)
        title, text = extract_text(html)
        docs.append(
            {
                "source": "blog",
                "author": author,
                "url": url,
                "date": datetime.now(timezone.utc).isoformat(),
                "raw_text": text,
                "title": title,
            }
        )
    return docs


if __name__ == "__main__":
    sample_urls: list[str] = []  # TODO: fill with your own post URLs
    results = crawl(sample_urls, author="me")
    print(f"Crawled {len(results)} blog posts")
