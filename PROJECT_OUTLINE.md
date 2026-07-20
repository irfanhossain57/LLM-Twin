# LLM Twin — Project Build Outline

Based on *LLM Engineer's Handbook* (Paul Iusztin & Maxime Labonne, Packt).
Reference implementation: https://github.com/PacktPublishing/LLM-Engineers-Handbook

The book organizes everything around the **FTI architecture** — three independent pipelines that communicate only through storage, never directly:

- **Feature pipeline** — turns raw writing into vectors in a vector DB
- **Training pipeline** — turns cleaned data into a fine-tuned model
- **Inference pipeline** — serves the twin, using the vector DB + fine-tuned model

Your repo should mirror this separation. It makes the project gradeable stage-by-stage and matches how the book's own repo is laid out.

---

## 1. Repo Structure

```
llm-twin/
├── README.md
├── .env.example
├── docker-compose.yml
├── pyproject.toml / requirements.txt
├── Makefile
│
├── data_collection/              # ETL — Chapter 3
│   ├── crawlers/
│   │   ├── blog_crawler.py
│   │   ├── linkedin_crawler.py
│   │   └── github_crawler.py
│   ├── dispatcher.py             # routes each source to its crawler
│   └── data_warehouse.py         # writes raw docs to Mongo/NoSQL store
│
├── feature_pipeline/             # cleaning → chunking → embedding — Chapter 4
│   ├── cdc.py                    # change data capture from warehouse
│   ├── cleaning.py
│   ├── chunking.py
│   ├── embedding.py
│   └── vector_db.py              # writes to Qdrant
│
├── training_pipeline/            # instruction dataset + fine-tuning — Ch. 5–6
│   ├── generate_instruct_dataset.py   # synthetic instruction generation
│   ├── dataset_versioning.py          # push to a dataset registry
│   ├── finetune.py                    # QLoRA/LoRA fine-tuning job
│   └── config/
│       └── training_config.yaml
│
├── inference_pipeline/           # RAG-grounded generation — Ch. 9
│   ├── query_expansion.py
│   ├── self_query.py             # metadata filter extraction
│   ├── retriever.py              # filtered vector search
│   ├── reranker.py
│   ├── prompt_templates.py
│   └── llm_twin_service.py       # ties retrieval + fine-tuned model together
│
├── evaluation/                   # golden sets, LLM-judge, monitoring — Ch. 7 & 11
│   ├── golden_dataset.json
│   ├── llm_judge.py
│   ├── metrics.py
│   └── monitoring/
│       └── opik_dashboard.py     # or whatever observability tool you pick
│
└── notebooks/
    ├── 01_explore_raw_data.ipynb
    ├── 02_inspect_chunks_embeddings.ipynb
    └── 03_eval_results.ipynb
```

---

## 2. Phase-by-Phase Breakdown

### Phase 1 — ETL (`data_collection/`)
- One crawler per source (blog, LinkedIn, GitHub), each normalizing into a common raw-document schema (`author`, `source`, `date`, `raw_text`, `url`).
- `dispatcher.py` picks the right crawler by URL/source type.
- `data_warehouse.py` persists everything to a single NoSQL store (Mongo is the book's choice) — this is your single source of truth for raw content.

### Phase 2 — Feature Pipeline (`feature_pipeline/`)
- `cdc.py`: watches the warehouse for new/changed docs (or just polls, for project scale).
- `cleaning.py`: strip markup/HTML, normalize whitespace, remove boilerplate.
- `chunking.py`: split into overlapping chunks sized for your embedding model's context.
- `embedding.py`: embed chunks (e.g., a sentence-transformer or an API embedding model).
- `vector_db.py`: upsert into Qdrant with metadata (source, date, author) for later filtering.

### Phase 3 — Training Pipeline (`training_pipeline/`)
- `generate_instruct_dataset.py`: for each cleaned doc/chunk, use an LLM to reverse-generate a plausible instruction that would produce that text — this is how you turn raw writing into (instruction, output) pairs without needing huge volume.
- `dataset_versioning.py`: log dataset versions (even a simple local versioning scheme is fine for a course project).
- `finetune.py`: QLoRA fine-tune a small open-weight model (e.g., in the Llama/Mistral/Qwen small-parameter range) on the instruction dataset.
- `training_config.yaml`: hyperparameters, base model, LoRA rank/alpha, etc.

### Phase 4 — Inference Pipeline (`inference_pipeline/`)
- `query_expansion.py`: generate multiple reformulations of the incoming query.
- `self_query.py`: extract metadata filters from the query (e.g., "only from my GitHub posts").
- `retriever.py`: run filtered vector search across the expanded queries, merge results.
- `reranker.py`: rerank retrieved chunks against the original query.
- `llm_twin_service.py`: assembles retrieved context + fine-tuned model into the final generation call.

### Phase 5 — Evaluation (`evaluation/`)
- `golden_dataset.json`: a small, hand-curated set of (query, ideal-answer) pairs — even 15–30 is fine.
- `llm_judge.py`: use a stronger LLM to score twin outputs against the golden set on style-fidelity, factual grounding, coherence.
- `metrics.py`: aggregate scores; define your production-readiness thresholds here.
- `monitoring/`: log live queries/outputs for drift and quality tracking over time.

---

## 3. Infra / Config Files

- **`.env.example`** — API keys, Qdrant URL, Mongo URI, model names
- **`docker-compose.yml`** — spin up Qdrant + Mongo locally
- **`requirements.txt` / `pyproject.toml`** — pin versions (transformers, peft, bitsandbytes, qdrant-client, pymongo, sentence-transformers, etc.)
- **`Makefile`** — shortcut commands: `make etl`, `make features`, `make train`, `make eval`, `make serve`

---

## 4. Deliverables Checklist

- [ ] ETL pipeline pulling from blog + LinkedIn + GitHub into a data warehouse
- [ ] Feature pipeline producing cleaned, chunked, embedded vectors in Qdrant
- [ ] Instruction dataset generated from your own content (with methodology documented)
- [ ] Fine-tuned open-weight model checkpoint (LoRA adapter is sufficient)
- [ ] Inference pipeline with query expansion, filtered retrieval, reranking
- [ ] Golden set + LLM-as-judge evaluation results
- [ ] Monitoring/logging setup, however minimal
- [ ] Write-up documenting the production-readiness gate decision (ship / don't ship, and why)
- [ ] Link to reference repo: https://github.com/PacktPublishing/LLM-Engineers-Handbook (with attribution noted for any adapted code)

---

## 5. Suggested Build Order (given your data volume constraint)

1. ETL + warehouse — get all three sources flowing into one place first, even if thin.
2. Feature pipeline — clean/chunk/embed everything; validate retrieval quality manually before touching fine-tuning.
3. Instruction dataset generation — this is where you spend the most effort given limited raw volume; iterate here before committing to a training run.
4. Fine-tuning — one solid LoRA run rather than multiple large ones; log it well.
5. Inference pipeline — wire retrieval + fine-tuned model together.
6. Evaluation — build the golden set last, once you've seen what real outputs look like, so your judging criteria are grounded in actual failure modes you observed.
