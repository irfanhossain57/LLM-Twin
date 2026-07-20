"""
LLM-as-judge: scores LLM Twin outputs against the golden set on
style-fidelity, factual grounding, and coherence.

`make eval` runs this module.
"""
import json
import os

from openai import OpenAI

from inference_pipeline.llm_twin_service import LLMTwin

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

JUDGE_PROMPT = """You are evaluating an AI-generated piece of writing that is
supposed to imitate a specific person's style, grounded in their own
past content.

QUERY: {query}
GENERATED OUTPUT: {output}

Score from 1-5 on each dimension and return strict JSON:
{{
  "style_fidelity": <1-5>,
  "factual_grounding": <1-5>,
  "coherence": <1-5>,
  "notes": "<one sentence>"
}}
"""


def judge_output(query: str, output: str, model: str = "gpt-4o-mini") -> dict:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(query=query, output=output)}],
        max_tokens=150,
    )
    try:
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        return {"style_fidelity": None, "factual_grounding": None, "coherence": None, "notes": "parse error"}


def run_evaluation(golden_path: str = "evaluation/golden_dataset.json") -> list[dict]:
    with open(golden_path, encoding="utf-8") as f:
        golden_set = json.load(f)

    twin = LLMTwin()
    results = []
    for item in golden_set:
        output = twin.answer(item["query"])
        scores = judge_output(item["query"], output)
        results.append({"query": item["query"], "output": output, **scores})

    return results


if __name__ == "__main__":
    results = run_evaluation()
    with open("evaluation/eval_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"[llm_judge] evaluated {len(results)} golden examples -> evaluation/eval_results.json")
