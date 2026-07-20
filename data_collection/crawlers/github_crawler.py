"""
Crawler for your own GitHub content: READMEs, PR descriptions,
commit messages, and code comments.

Uses the GitHub REST API. Set GITHUB_TOKEN in your environment
for higher rate limits.
"""
import os
from datetime import datetime, timezone

import requests

GITHUB_API = "https://api.github.com"


def _headers() -> dict:
    token = os.getenv("GITHUB_TOKEN")
    return {"Authorization": f"token {token}"} if token else {}


def fetch_repo_readme(owner: str, repo: str) -> dict | None:
    """Fetch the README of a repo as a raw document."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/readme"
    resp = requests.get(url, headers={**_headers(), "Accept": "application/vnd.github.raw"})
    if resp.status_code != 200:
        return None
    return {
        "source": "github",
        "author": owner,
        "url": f"https://github.com/{owner}/{repo}",
        "date": datetime.now(timezone.utc).isoformat(),
        "raw_text": resp.text,
        "title": f"{repo} README",
    }


def fetch_commit_messages(owner: str, repo: str, author: str, limit: int = 100) -> list[dict]:
    """Fetch recent commit messages authored by `author` in a repo."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"
    resp = requests.get(url, headers=_headers(), params={"author": author, "per_page": limit})
    resp.raise_for_status()
    docs = []
    for commit in resp.json():
        message = commit["commit"]["message"]
        docs.append(
            {
                "source": "github",
                "author": author,
                "url": commit.get("html_url", ""),
                "date": commit["commit"]["author"]["date"],
                "raw_text": message,
                "title": "commit message",
            }
        )
    return docs


def crawl(owner: str, repos: list[str], author: str) -> list[dict]:
    """Crawl READMEs + commit messages across a list of repos."""
    docs: list[dict] = []
    for repo in repos:
        readme = fetch_repo_readme(owner, repo)
        if readme:
            docs.append(readme)
        docs.extend(fetch_commit_messages(owner, repo, author))
    return docs


if __name__ == "__main__":
    sample_repos: list[str] = []  # TODO: fill with your own repo names
    results = crawl(owner="me", repos=sample_repos, author="me")
    print(f"Crawled {len(results)} GitHub documents")
