# PLN-RAG MetaMo Integration

This repository combines:
- `MetaMo-Prototype`: motivation-driven routing and response pipeline
- `PLN-RAG`: ingestion, retrieval, and PLN reasoning service
- `Qwestor-frontend`: Vite/React frontend for chat and PLN tools

The main integration path is:
- MetaMo `/chat` receives user query
- MetaMo routes action (`act_search`, `act_think`, etc.)
- For search/synthesis flows, MetaMo can search/scrape and ingest into PLN-RAG
- For think flows, MetaMo can query PLN-RAG and include reasoning output

## Repository Structure

- `MetaMo-Prototype/`: API, routing engine, runner/eval scripts, logs
- `PLN-RAG/`: PLN service (FastAPI), Qdrant integration, ingest/query endpoints
- `Qwestor-frontend/`: React frontend for chat, ingest, query, reset, and health flows

## Prerequisites

- Docker Desktop with Compose
- API keys configured in env files as needed
- Optional: local Python venv only if you want to run services outside Docker

## Run the Integrated Stack (Docker)

From:
`PLN_RAG MetaMo Integration/MetaMo-Prototype`

1. Configure environment
- Copy `.env.example` to `.env`
- Fill required values (LLM provider keys, PLN settings)

2. Build services
```bash
docker compose build
```

3. Start services
```bash
docker compose up
```

This compose starts:
- `qdrant`
- `pln-rag`
- `metamo` (API mode)

## Run the Frontend

From:
`PLN_RAG MetaMo Integration/Qwestor-frontend`

1. Install dependencies
```bash
pnpm install
```

2. Configure frontend environment
```bash
cp .env.example .env
```

3. Start the dev server
```bash
pnpm dev
```

The frontend uses:
- `VITE_METAMO_BASE_URL=http://localhost:8010`
- `VITE_PLNRAG_BASE_URL=http://localhost:8001`

It also supports Vite proxy fallbacks for `/metamo` and `/plnrag`.

## Service Endpoints

MetaMo API (for frontend):
- `http://localhost:8010/health`
- `http://localhost:8010/docs`
- `POST http://localhost:8010/chat`

PLN-RAG (internal + optional direct debug):
- `http://localhost:8001/health`
- `http://localhost:8001/docs`

Qdrant:
- `http://localhost:6333/dashboard`

Frontend:
- Vite dev server URL shown by `pnpm dev`

## Chat API Contract (Frontend)

Request:
```json
{
  "query": "Search for recent OpenAI updates",
  "session_id": "user-123"
}
```

Response:
```json
{
  "session_id": "user-123",
  "action": "act_search",
  "answer": "...",
  "decision": {},
  "context": {}
}
```

Notes:
- `session_id` controls conversation continuity.
- Reusing the same `session_id` reuses engine state.
- New `session_id` starts a fresh conversation state.

## Logging

MetaMo writes logs under:
- `MetaMo-Prototype/logs/run_YYYYMMDD_HHMMSS/`

Includes:
- `turns.json`
- `turns.csv`
- `run_meta.json`
- `scraped_debug/` (search scrape snapshots when available)

## Offline Evaluation (Runner)

Runner-based session tests are still supported and unchanged.

From `MetaMo-Prototype/`:
```bash
python runner.py
```

Use this for strict/soft action accuracy benchmarking.

