"""
Instruction dataset generation: reverse-engineers plausible
(instruction, output) pairs from your own cleaned content, so a
small raw corpus can be turned into a larger fine-tuning dataset.

Approach: for each cleaned document/chunk, ask a strong LLM
"what prompt would have produced this text?" and pair the generated
instruction with the ORIGINAL text as the target output. This keeps
the training target in your real voice while only synthesizing the
instruction side.
"""
import json
import os

from openai import OpenAI

from data_collection.data_warehouse import load_all_documents
from feature_pipeline.cleaning import clean_documents

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INSTRUCTION_GEN_PROMPT = """You will be shown a piece of someone's own writing.
Write ONE short, natural instruction/prompt that could plausibly have led
them to write this text (e.g. "Write a LinkedIn post about X").
Return only the instruction, nothing else.

TEXT:
{text}
"""


def generate_instruction(text: str, model: str = "gpt-4o-mini") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": INSTRUCTION_GEN_PROMPT.format(text=text)}],
        max_tokens=60,
    )
    return response.choices[0].message.content.strip()


def build_dataset(min_chars: int = 40) -> list[dict]:
    """
    Build the instruction dataset from all cleaned documents.

    Documents/chunks shorter than `min_chars` are skipped -- too short
    to carry meaningful style signal.
    """
    raw_docs = load_all_documents()
    cleaned = clean_documents(raw_docs)

    dataset = []
    for doc in cleaned:
        text = doc["clean_text"]
        if len(text) < min_chars:
            continue
        instruction = generate_instruction(text)
        dataset.append(
            {
                "instruction": instruction,
                "output": text,
                "source": doc["source"],
                "url": doc["url"],
            }
        )
    return dataset


def save_dataset(dataset: list[dict], path: str = "training_pipeline/instruct_dataset.jsonl") -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in dataset:
            f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    ds = build_dataset()
    save_dataset(ds)
    print(f"[training_pipeline] generated {len(ds)} instruction pairs")
