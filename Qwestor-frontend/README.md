# Qwestor Frontend

A clean React frontend for Qwestor, an AI-powered research assistant chatbot.

## Setup

1. Install dependencies:

   ```bash
   pnpm install
   ```

2. Configure API URLs:

   ```bash
   cp .env.example .env
   ```

   Defaults:
   - `VITE_METAMO_BASE_URL=http://localhost:8010`
   - `VITE_PLNRAG_BASE_URL=http://localhost:8001`

3. Start the development server:

   ```bash
   pnpm dev
   ```

## API Integration

- MetaMo chat endpoint: `${VITE_METAMO_BASE_URL}/chat`
- PLN-RAG endpoints:
  - `${VITE_PLNRAG_BASE_URL}/ingest`
  - `${VITE_PLNRAG_BASE_URL}/query`
  - `${VITE_PLNRAG_BASE_URL}/reset`
  - `${VITE_PLNRAG_BASE_URL}/health`

## Features

- Chat with per-thread `session_id` continuity
- PLN-RAG ingest panel for batch text ingestion
- PLN-RAG query panel with structured response fields
- PLN-RAG reset controls by scope (`all`, `vectordb`, `atomspace`)
- PLN-RAG health status panel
