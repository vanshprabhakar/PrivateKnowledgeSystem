# Multi-Knowledge-Base RAG System

Production-oriented, config-driven RAG platform for enterprise deployment with per-KB collections in ChromaDB and local LLM inference via Ollama.

## Features
- Config-driven KB and source mapping (`config/config.yaml`)
- Single-KB and multi-KB querying
- Source-aware retrieval filters (`kb`, `source`, `top_k`)
- Pluggable ingestion modules for Confluence, GitHub, SharePoint, Tableau
- Tableau REST API ingestion for workbooks, dashboards/views, and data sources
- Local embedding (`sentence-transformers`) + local generation (`Ollama`)
- API (`FastAPI`), CLI, and Streamlit dashboard
- Retry logic for ingestion failures

## Project Structure
See code tree under:
- `config/`
- `ingestion/`
- `processing/`
- `embeddings/`
- `vectorstore/`
- `retrieval/`
- `llm/`
- `orchestrator/`
- `api/`
- `scripts/`
- `ui/`
- `query.py`

## Installation
```bash
cd knowledge-ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick local test (fastest path)
If you want to test end-to-end quickly without wiring enterprise connectors first:

```bash
# 1) install dependencies
pip install -r requirements.txt

# 2) ensure Ollama is running locally and model is available
ollama pull mistral
ollama serve

# 3) load demo docs into all KB collections
python scripts/load_demo_data.py

# 4) query from CLI
python query.py --kb engineering_kb "How does payroll integration work?"
```

## Configuration
Edit `config/config.yaml`:
- Add/remove KBs under `knowledge_bases`
- Enable/disable sources per KB via `sources` list
- Tune chunking, models, top_k, retries in `global_settings`

### Add a new knowledge base (no code changes)
1. Add new key under `knowledge_bases`.
2. Set `sources` using any supported connector: `confluence`, `github`, `sharepoint`, `tableau`.
3. Run ingestion for that KB.

## Credentials
Use environment variables (never hardcode secrets):
- Tableau (required by `tableau` connector):
  - `TABLEAU_SERVER`
  - `TABLEAU_USERNAME`
  - `TABLEAU_PASSWORD`
  - `TABLEAU_SITE_CONTENT_URL` (optional)
  - `TABLEAU_API_VERSION` (optional, default `3.24`)

Confluence/GitHub/SharePoint connectors are scaffolded for enterprise API credentials and should be wired to your infra auth model.

## Ingestion
### Ingest one KB
```bash
python scripts/ingest_kb.py --kb engineering_kb
```

### Ingest all KBs
```bash
python scripts/ingest_all.py
```

## Query
### CLI
```bash
python query.py --kb engineering_kb "How does payroll integration work?"
python query.py --kb engineering_kb finance_kb --source tableau "Show revenue dashboard lineage"
python query.py "What is the PTO policy?"
```

### API
```bash
uvicorn api.main:app --reload --port 8000
```

POST `/query`
```json
{
  "query": "How does payroll integration work?",
  "kb": ["engineering_kb", "finance_kb"],
  "source": ["github", "tableau"],
  "top_k": 5
}
```

## Dashboard (UI/UX)
Run a local dashboard with ingestion buttons, KB/source filters, and rich context viewers:

```bash
streamlit run ui/dashboard.py
```

Dashboard highlights:
- Multi-select KB querying (single, multi, all)
- Source filter and `top_k` controls
- One-click ingest selected KB or all KBs
- Expandable result cards showing source metadata and content

## Guardrails
- Generator prompt enforces context-only answers.
- If no supporting context: `Not found in selected knowledge base(s)`.
- Local execution path for embeddings and LLM inference.
- Secrets handled via environment variables.

## Notes for Production Hardening
- Implement real source APIs in Confluence/GitHub/SharePoint connectors.
- Add incremental sync checkpoint persistence (e.g., per-source watermark).
- Add authN/authZ around API endpoints.
- Add structured logging and metrics export.
