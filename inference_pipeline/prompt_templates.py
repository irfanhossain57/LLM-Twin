"""
Prompt templates: assembles the final generation prompt from retrieved
context and the user's query.
"""

SYSTEM_PROMPT = """You are an LLM Twin: you write exactly like the person
whose content is shown to you as context. Match their tone, phrasing
habits, and structure. Use the context to ground any facts -- do not
invent claims that aren't supported by it.
"""

USER_PROMPT_TEMPLATE = """CONTEXT (your own past writing):
{context}

TASK:
{query}
"""


def build_prompt(query: str, context_chunks: list[dict]) -> list[dict]:
    context = "\n\n---\n\n".join(c["text"] for c in context_chunks)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(context=context, query=query)},
    ]
