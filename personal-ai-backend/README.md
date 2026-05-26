# Personal AI — Backend

Intelligent API that replaces 14 n8n workflows with Python agents using LangChain/LangGraph + GPT-4o + PostgreSQL.

## Stack

- **Framework:** FastAPI
- **Orchestration:** LangGraph (StateGraph)
- **LLM:** OpenAI GPT-4o via `langchain-openai`
- **Modeling:** Pydantic v2
- **Database:** PostgreSQL 16 via asyncpg
- **Bot:** Telegram via aiogram (optional)
- **Containerization:** Docker Compose (backend + PostgreSQL + frontend)

## Structure

```
src/
  main.py              # FastAPI entrypoint (6 endpoints)
  config.py            # Config via pydantic-settings + .env
  agents/
    router.py          # WF-16: classifies intent, executes sub-graphs, synthesizes
    clinical.py        # WF-01..03,07,08,13: clinical chains with GPT-4o
    scoring.py         # WF-04..06,09..11,14: deterministic scoring algorithms
    conversational.py  # WF-12: chat with LangGraph + checkpointing (memory)
  db/
    schema.sql         # PostgreSQL schema (10 tables, English enums)
    connection.py      # asyncpg pool manager
    repository.py      # Repository functions replacing n8n mock JSONs
    seed.py            # Faker seed script (50 patients, English)
    init_schema.py     # Schema migration script
  tools/
    llm_tools.py       # GPT-4o prompts and chains (6 chains)
    scoring_tools.py   # Scoring algorithms migrated from n8n JS
  models/              # Pydantic schemas (clinical, financial, operational)
  channels/
    telegram.py        # Telegram bot (aiogram, disabled without token)
tests/
  test_scoring.py      # Unit tests for scoring algorithms
```

## Endpoints

| Method | Route           | Description                                       |
|--------|-----------------|---------------------------------------------------|
| GET    | `/health`       | Health check                                      |
| POST   | `/workflow`     | Execute clinical or scoring workflow              |
| POST   | `/chat`         | Conversational copilot (with memory)              |
| POST   | `/dashboard`    | Voice dashboard (classify + execute + summarize)  |
| GET    | `/workflows`    | List available workflows and dashboards           |

## Workflows

**Clinical (GPT-4o):** `resumo_prontuario` (chart summary), `sumarizacao_evolucao` (evolution summarization), `insights_dashboard` (KPI insights), `documentacao_clinica` (clinical documentation), `copilot_regulatorio` (regulatory copilot), `followup_pos_alta` (post-discharge follow-up)

**Scoring (deterministic):** `priorizacao_filas` (queue prioritization), `predicao_glosa` (denial prediction), `predicao_noshow` (no-show prediction), `conferencia_documental` (document review), `agendamento_cirurgico` (surgical scheduling), `gargalos` (bottleneck detection), `monitoramento` (KPI monitoring)

**Dashboards:** `executivo` (executive), `financeiro` (financial), `regulatorio` (regulatory), `operacional` (operational), `agenda` (scheduling)

## Quick Start (Docker)

```bash
git clone <repo>
cd personal-ai-backend

# Create .env with your keys
echo "OPENAI_API_KEY=sk-..." > .env

# Start all services
docker compose up -d

# Backend: http://localhost:8000
# Swagger: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

The first start creates the PostgreSQL schema, seeds 50 sample patients, and starts the API.

## Local Development

```bash
# Requires PostgreSQL 16 running locally
# Configure DATABASE_URL in .env

pip install -e .
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Note: `--reload` does not work reliably on Windows (WatchFiles + multiprocessing pipe). On Docker Linux it works fine.

## Environment Variables

| Variable         | Default                                                   | Description          |
|------------------|-----------------------------------------------------------|----------------------|
| `DATABASE_URL`   | `postgresql://personalai:personalai_secret@localhost:5432/personalai` | PostgreSQL DSN |
| `OPENAI_API_KEY` | —                                                         | OpenAI API key       |
| `OPENAI_MODEL`   | `gpt-4o`                                                  | Model name           |
| `TELEGRAM_BOT_TOKEN` | —                                                     | Telegram bot (optional) |

## Tests

```bash
pytest tests/
```
