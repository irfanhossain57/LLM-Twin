"""
Self-query: extracts metadata filters (source, date range, author)
from the user's natural-language query, so retrieval can be scoped
(e.g. "only from my GitHub posts").
"""
import json
import os

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SELF_QUERY_PROMPT = """Extract any metadata filters implied by this query.
Valid sources: "blog", "linkedin", "github".
Return strict JSON: {{"source": <str or null>}}
No other text.

QUERY: {query}
"""


def extract_filters(query: str, model: str = "gpt-4o-mini") -> dict:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": SELF_QUERY_PROMPT.format(query=query)}],
        max_tokens=50,
    )
    try:
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        return {"source": None}
