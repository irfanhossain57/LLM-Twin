"""
Fine-tuning: QLoRA fine-tune a small open-weight model on the
instruction dataset so it adopts your writing style.

`make train` runs this module.
"""
import json
import os

import torch
import yaml
from datasets import Dataset
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
)

CONFIG_PATH = "training_pipeline/config/training_config.yaml"
DATASET_PATH = "training_pipeline/instruct_dataset.jsonl"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def load_dataset(tokenizer) -> Dataset:
    rows = []
    with open(DATASET_PATH, encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    def format_example(row: dict) -> str:
        return f"### Instruction:\n{row['instruction']}\n\n### Response:\n{row['output']}"

    texts = [format_example(r) for r in rows]
    encodings = tokenizer(texts, truncation=True, padding="max_length", max_length=512)
    return Dataset.from_dict(encodings)


def run() -> None:
    config = load_config()
    base_model_name = os.getenv("BASE_MODEL_NAME", config["base_model_name"])

    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(base_model_name, quantization_config=bnb_config)

    lora_config = LoraConfig(
        r=config["lora"]["r"],
        lora_alpha=config["lora"]["alpha"],
        target_modules=config["lora"]["target_modules"],
        lora_dropout=config["lora"]["dropout"],
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    dataset = load_dataset(tokenizer)

    training_args = TrainingArguments(
        output_dir=config["output_dir"],
        num_train_epochs=config["num_train_epochs"],
        per_device_train_batch_size=config["batch_size"],
        learning_rate=config["learning_rate"],
        logging_steps=10,
        save_strategy="epoch",
    )

    trainer = Trainer(model=model, args=training_args, train_dataset=dataset)
    trainer.train()
    model.save_pretrained(config["output_dir"])
    tokenizer.save_pretrained(config["output_dir"])
    print(f"[finetune] saved LoRA adapter to {config['output_dir']}")


if __name__ == "__main__":
    run()
