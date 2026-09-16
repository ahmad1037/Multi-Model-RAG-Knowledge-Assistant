# Multimodal RAG Knowledge Assistant

A production-oriented Full-Stack Multimodal Retrieval-Augmented
Generation platform for searching and reasoning over text,
documents, charts, diagrams, screenshots, and images.

## Planned Capabilities

- React + TypeScript frontend
- FastAPI REST backend
- PostgreSQL + pgvector
- Document ingestion
- Text embeddings
- Hybrid retrieval
- CLIP cross-modal retrieval
- ColPali visual document retrieval
- Reranking
- Vision-language understanding
- Grounded LLM generation
- Source attribution
- RAG evaluation
- Docker
- GitHub Actions
- AWS deployment

## Current Status

Milestone 1 — Platform foundation

## Tests

Run the normal backend suite from the repository root:

```powershell
uv run --project backend pytest -q backend/tests
```

These tests mock database access and model inference. CI runs them on a standard
runner with Hugging Face offline mode enabled; it does not need PostgreSQL, a GPU,
Ollama, or model weights. Scripts named `backend/scripts/smoke_*.py` are manual
model checks and are outside the normal test suite.
