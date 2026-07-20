"""
LLM Twin service: ties retrieval + reranking + the fine-tuned model
together into a single callable inference pipeline.

`make serve` runs this module.
"""
import os

from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from inference_pipeline.prompt_templates import build_prompt
from inference_pipeline.reranker import rerank
from inference_pipeline.retriever import retrieve

ADAPTER_PATH = "training_pipeline/checkpoints/llm-twin-lora"


class LLMTwin:
    def __init__(self):
        base_model_name = os.getenv("BASE_MODEL_NAME", "meta-llama/Llama-3.2-3B-Instruct")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        base_model = AutoModelForCausalLM.from_pretrained(base_model_name)
        self.model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
        self.generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    def answer(self, query: str) -> str:
        candidates = retrieve(query, top_k=10)
        top_chunks = rerank(query, candidates, top_k=3)
        messages = build_prompt(query, top_chunks)

        prompt_text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        output = self.generator(prompt_text, max_new_tokens=300, do_sample=True, temperature=0.7)
        return output[0]["generated_text"][len(prompt_text):].strip()


if __name__ == "__main__":
    twin = LLMTwin()
    while True:
        query = input("\nAsk your LLM Twin something (Ctrl+C to quit): ")
        print("\n" + twin.answer(query))
