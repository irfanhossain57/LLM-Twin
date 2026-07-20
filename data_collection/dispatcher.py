"""
Dispatcher: routes each configured source to its crawler, then persists
everything into the data warehouse. This is the ETL entry point --
`make etl` runs this module.
"""
from data_collection.crawlers import blog_crawler, github_crawler, linkedin_crawler
from data_collection.data_warehouse import save_documents

AUTHOR = "me"  # TODO: replace with your name/handle

# TODO: fill these in with your own content sources
BLOG_URLS: list[str] = []
LINKEDIN_EXPORT_DIR = "./linkedin_export"
GITHUB_OWNER = "me"
GITHUB_REPOS: list[str] = []


def run() -> None:
    all_docs: list[dict] = []

    if BLOG_URLS:
        all_docs.extend(blog_crawler.crawl(BLOG_URLS, author=AUTHOR))

    try:
        all_docs.extend(linkedin_crawler.load_linkedin_export(LINKEDIN_EXPORT_DIR, author=AUTHOR))
    except FileNotFoundError as e:
        print(f"[dispatcher] skipping LinkedIn: {e}")

    if GITHUB_REPOS:
        all_docs.extend(github_crawler.crawl(GITHUB_OWNER, GITHUB_REPOS, author=AUTHOR))

    written = save_documents(all_docs)
    print(f"[dispatcher] collected {len(all_docs)} docs, wrote {written} to warehouse")


if __name__ == "__main__":
    run()
