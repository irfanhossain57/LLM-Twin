# LLM Twin

An AI character that writes in your own voice, grounded via RAG on your own
writing (blog, LinkedIn, GitHub) and adapted to your style via fine-tuning.

Built following the FTI (Feature / Training / Inference) architecture from
*LLM Engineer's Handbook* (Paul Iusztin & Maxime Labonne, Packt).

Reference implementation: https://github.com/PacktPublishing/LLM-Engineers-Handbook
Portions of this project are adapted from the above repository under its
license terms; see NOTICE for attribution details.

## Pipelines

| Pipeline | Folder | Responsibility |
|---|---|---|
| ETL | `data_collection/` | Crawl your own content into a data warehouse |
| Feature | `feature_pipeline/` | Clean, chunk, embed into a vector DB |
| Training | `training_pipeline/` | Generate instruction data, fine-tune a model |
| Inference | `inference_pipeline/` | Query expansion, retrieval, reranking, generation |
| Evaluation | `evaluation/` | Golden set, LLM-as-judge, monitoring |

## Quickstart

```bash
cp .env.example .env          # fill in your keys / connection strings
docker compose up -d          # start Qdrant + Mongo
pip install -r requirements.txt

make etl        # crawl your content into the warehouse
make features    # clean, chunk, embed into Qdrant
make dataset     # generate the instruction dataset
make train       # fine-tune the model
make eval        # run the golden set through the LLM judge
make serve       # start the inference service
```

See `PROJECT_OUTLINE.md` for the full phase-by-phase design notes.
