"""
Query expansion: generates multiple reformulations of the incoming
query so retrieval isn't limited to one phrasing.
"""
import os

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EXPANSION_PROMPT = """Generate {n} different ways to phrase this search query,
each capturing a different angle a relevant document might match on.
Return one per line, no numbering.

QUERY: {query}
"""


def expand_query(query: str, n: int = 3, model: str = "gpt-4o-mini") -> list[str]:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": EXPANSION_PROMPT.format(query=query, n=n)}],
        max_tokens=150,
    )
    lines = response.choices[0].message.content.strip().splitlines()
    variants = [line.strip("- ").strip() for line in lines if line.strip()]
    return [query] + variants[:n]
