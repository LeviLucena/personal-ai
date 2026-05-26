# Personal AI — Unified Documentation

![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white) ![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white) ![OpenAI](https://img.shields.io/badge/OpenAI_GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white) ![asyncpg](https://img.shields.io/badge/asyncpg-336791?style=for-the-badge&logo=postgresql&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![Telegram Bot](https://img.shields.io/badge/Telegram_Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white) ![React](https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black) ![TanStack Start](https://img.shields.io/badge/TanStack_Start-FF4154?style=for-the-badge&logo=tanstack&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript_5-3178C6?style=for-the-badge&logo=typescript&logoColor=white) ![Vite](https://img.shields.io/badge/Vite_7-646CFF?style=for-the-badge&logo=vite&logoColor=white) ![Cloudflare](https://img.shields.io/badge/Cloudflare_Workers-F38020?style=for-the-badge&logo=cloudflare&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS_v4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white) ![Radix UI](https://img.shields.io/badge/Radix_UI-161618?style=for-the-badge&logo=radixui&logoColor=white) ![Framer Motion](https://img.shields.io/badge/Framer_Motion-0055FF?style=for-the-badge&logo=framer&logoColor=white) ![Simli](https://img.shields.io/badge/Simli_Avatar-635BFF?style=for-the-badge&logo=heygen&logoColor=white) ![Zod](https://img.shields.io/badge/Zod-3E67B1?style=for-the-badge&logo=zod&logoColor=white) ![React Hook Form](https://img.shields.io/badge/React_Hook_Form-EC5990?style=for-the-badge&logo=reacthookform&logoColor=white) ![Recharts](https://img.shields.io/badge/Recharts-22B5BF?style=for-the-badge&logo=recharts&logoColor=white)

AI-powered hospital management platform. Replaces 14 n8n workflows with Python agents (LangChain/LangGraph + GPT-4o) and a modern React frontend with voice interaction and digital avatar.

---

## Table of Contents

1. [Repositories Overview](#1-repositories-overview)
2. [System Flow](#2-system-flow)
3. [Backend](#3-backend)
   - [Stack](#31-stack)
   - [Structure](#32-structure)
   - [Endpoints](#33-endpoints)
   - [Workflows](#34-workflows)
   - [Setup](#35-setup)
   - [Environment Variables](#36-environment-variables)
   - [Tests](#37-tests)
4. [Frontend](#4-frontend)
   - [Stack](#41-stack)
   - [Structure](#42-structure)
   - [Workflows](#43-workflows)
   - [Setup](#44-setup)
   - [Scripts](#45-scripts)
   - [Notes](#46-notes)
5. [Architecture](#5-architecture)
   - [Overall Architecture](#51-overall-architecture)
   - [Data Flow](#52-data-flow)
   - [Workflow Mapping](#53-workflow-mapping)
   - [Database](#54-database)
   - [Docker Setup](#55-docker-setup)
   - [Deployment](#56-deployment)
   - [Technical Notes](#57-technical-notes)
   - [n8n Migration Summary](#58-n8n-migration-summary)
6. [n8n vs Python Comparison](#6-n8n-vs-python-comparison)
   - [Comparison Table](#61-comparison-table)
   - [Pros and Cons](#62-pros-and-cons)
   - [Credentials and Security](#63-credentials-and-security)
   - [When to Use Each](#64-when-to-use-each)
   - [Real Project Numbers](#65-real-project-numbers)
7. [Quick Start](#7-quick-start)

---

## 1. Repositories Overview

```
personal-ai-backend/   → Python API (FastAPI + LangChain/LangGraph + PostgreSQL)
personal-ai-frontend/  → React SPA (TanStack Start + Tailwind v4)
```

---

## 2. System Flow

```mermaid
flowchart TD
    A[User accesses Personal AI] --> B[Initial state - orb idle]
    B --> C{User speaks or types?}

    C -->|No| D[Orb waits for interaction]
    C -->|Yes| E[Set orb to listening]

    E --> F[Capture audio or text input]
    F --> G[Detect workflow via keywords]

    G --> H{Workflow type}

    H -->|clinical| I[POST /workflow]
    H -->|scoring| I
    H -->|conversational| J[POST /chat]
    H -->|dashboard| K[POST /dashboard]

    I --> L[Router Graph: classify intent]
    L --> M{Graph type}

    M -->|Clinical| N[Clinical Graph - GPT-4o chains]
    M -->|Scoring| O[Scoring Graph - deterministic]

    N --> P[Query PostgreSQL via asyncpg]
    O --> P

    J --> Q[Conversational Graph - LangGraph memory]
    Q --> P

    K --> R[Router Graph: classify + execute]
    R --> S[Run sub-graphs - insights + monitoring]
    S --> T[Synthesize response with GPT-4o]

    P --> U[Repository layer: patients, evolutions, bills, KPIs]
    U --> V[Return structured data to agent]

    V --> W[Agent formats response]
    T --> W
    W --> X[Return to frontend]

    X --> Y[Transform response via transformResponse]
    Y --> Z[Render in ResponseRenderer]

    Z --> AA[Send text to OpenAI TTS]
    AA --> AB[Stream audio to Simli avatar]
    AB --> AC[Set orb to speaking]

    AC --> AD[Display response in ResponseSheet]
    AD --> AE{User asks another question?}

    AE -->|Yes| C
    AE -->|No| B
```

> **SVG export:** Copy the Mermaid block above to [mermaid.live](https://mermaid.live) or use the CLI: `mmdc -i UNIFIED.md -o architecture.svg -t dark -b transparent`

---

## 3. Backend

### 3.1 Stack

- **Framework:** FastAPI
- **Orchestration:** LangGraph (StateGraph)
- **LLM:** OpenAI GPT-4o via `langchain-openai`
- **Modeling:** Pydantic v2
- **Database:** PostgreSQL 16 via asyncpg
- **Bot:** Telegram via aiogram (optional)
- **Containerization:** Docker Compose (backend + PostgreSQL + frontend)

### 3.2 Structure

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

### 3.3 Endpoints

| Method | Route           | Description                                       |
|--------|-----------------|---------------------------------------------------|
| GET    | `/health`       | Health check                                      |
| POST   | `/workflow`     | Execute clinical or scoring workflow              |
| POST   | `/chat`         | Conversational copilot (with memory)              |
| POST   | `/dashboard`    | Voice dashboard (classify + execute + summarize)  |
| GET    | `/workflows`    | List available workflows and dashboards           |

### 3.4 Workflows

**Clinical (GPT-4o):** `resumo_prontuario` (chart summary), `sumarizacao_evolucao` (evolution summarization), `insights_dashboard` (KPI insights), `documentacao_clinica` (clinical documentation), `copilot_regulatorio` (regulatory copilot), `followup_pos_alta` (post-discharge follow-up)

**Scoring (deterministic):** `priorizacao_filas` (queue prioritization), `predicao_glosa` (denial prediction), `predicao_noshow` (no-show prediction), `conferencia_documental` (document review), `agendamento_cirurgico` (surgical scheduling), `gargalos` (bottleneck detection), `monitoramento` (KPI monitoring)

**Dashboards:** `executivo` (executive), `financeiro` (financial), `regulatorio` (regulatory), `operacional` (operational), `agenda` (scheduling)

### 3.5 Setup

#### Docker (recommended)

```bash
git clone <repo>
cd personal-ai-backend
echo "OPENAI_API_KEY=sk-..." > .env
docker compose up -d
```

The first start creates the PostgreSQL schema, seeds 50 sample patients, and starts the API.

#### Local Development

```bash
pip install -e .
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

> Note: `--reload` does not work reliably on Windows (WatchFiles + multiprocessing pipe). On Docker Linux it works fine.

### 3.6 Environment Variables

| Variable            | Default                                                   | Description          |
|---------------------|-----------------------------------------------------------|----------------------|
| `DATABASE_URL`      | `postgresql://personalai:personalai_secret@localhost:5432/personalai` | PostgreSQL DSN |
| `OPENAI_API_KEY`    | —                                                         | OpenAI API key       |
| `OPENAI_MODEL`      | `gpt-4o`                                                  | Model name           |
| `TELEGRAM_BOT_TOKEN`| —                                                         | Telegram bot (optional) |

### 3.7 Tests

```bash
pytest tests/
```

---

## 4. Frontend

### 4.1 Stack

- **Framework:** React 19 + TanStack Start (SPA)
- **Routing:** TanStack Router
- **Styling:** Tailwind CSS v4 + shadcn/ui
- **Animation:** Framer Motion
- **Avatar:** Simli (digital avatar with audio streaming)
- **Voice:** Web Speech API (recognition) + OpenAI TTS (synthesis)
- **Build:** Vite + Cloudflare Workers (deploy)
- **Backend:** FastAPI + PostgreSQL (via Docker Compose)

### 4.2 Structure

```
src/
  routes/
    __root.tsx      # Root layout, SEO, 404
    index.tsx       # Main page (orb, input, microphone, response)
    panel.tsx       # Detachable panel with auto-refresh (30s/1min/5min)
  components/
    personal-ai/
      Orb.tsx              # Animated orb (4 states: idle, listening, processing, speaking)
      InputPill.tsx        # Styled input with microphone
      ResponseRenderer.tsx # Renders all workflow responses
      ResponseSheet.tsx    # Animated sheet for displaying responses
      AvatarStream.tsx     # Audio/video streaming for Simli avatar
      HelpModal.tsx        # Modal with example queries
    ui/                    # shadcn/ui components
  lib/
    personal-ai-workflows.ts  # Workflow mapping (URL, buildBody, transformResponse)
    voice-ai.ts               # TTS pipeline (OpenAI → audio → Simli)
    utils.ts                  # Utilities (cn)
  hooks/
    use-speech-recognition.ts # Web Speech API hook
    use-mobile.tsx            # Mobile detection
  styles.css               # Theme with oklch variables
```

### 4.3 Workflows

| Tag    | Feature               | Backend               | Description                           |
|--------|-----------------------|-----------------------|---------------------------------------|
| WF-16  | Voice dashboard       | `POST /dashboard`     | Status, risks, bottlenecks, etc       |
| WF-12  | Conversational copilot| `POST /chat`          | Questions about hospital data         |
| WF-07  | Clinical documentation| `POST /workflow`      | Generate progress notes               |
| WF-08  | Regulatory copilot    | `POST /workflow`      | Authorization justifications          |

Workflow detection is automatic based on keywords in the user's input.

### 4.4 Setup

```bash
cd personal-ai-frontend

# Copy and edit .env
VITE_API_BASE_URL=http://localhost:8000
VITE_SIMLI_API_KEY=...
VITE_SIMLI_FACE_ID=...
VITE_OPENAI_API_KEY=...

npm install
npm run dev
```

### 4.5 Scripts

| Command            | Description                    |
|--------------------|--------------------------------|
| `npm run dev`      | Dev server with HMR            |
| `npm run build`    | Production build (client+SSR)  |
| `npm run preview`  | Preview the build              |
| `npm run lint`     | ESLint                         |
| `npm run format`   | Prettier                       |

### 4.6 Notes

- The frontend expects the backend at `VITE_API_BASE_URL` (default: `http://localhost:8000`).
- Simli avatar requires valid `VITE_SIMLI_API_KEY` and `VITE_SIMLI_FACE_ID`.
- Deployment uses Cloudflare Workers (config in `wrangler.jsonc`).

---

## 5. Architecture

### 5.1 Overall Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React SPA)                          │
│  TanStack Start · Tailwind v4 · shadcn/ui · Framer Motion            │
│                                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Orb    │  │  Input   │  │  Avatar       │  │  Response        │  │
│  │ (state)  │  │(voice+txt)│  │  Simli (TTS)  │  │  Renderer        │  │
│  └──────────┘  └──────────┘  └──────────────┘  └──────────────────┘  │
│                        │ HTTP (fetch)                                 │
└────────────────────────┼──────────────────────────────────────────────┘
                         │ POST /workflow · /chat · /dashboard
                         ▼
┌───────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI + LangGraph)                     │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                    Router Graph (WF-16)                        │   │
│  │  classify → [sub-graphs] → synthesize response                │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                    │ dispatches to                                    │
│        ┌───────────┼───────────┬───────────────────┐                 │
│        ▼           ▼           ▼                   ▼                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐         │
│  │ Clinical │ │ Scoring  │ │ Conversa-│ │ LLM Tools        │         │
│  │ Graph    │ │ Graph    │ │ tional   │ │ (GPT-4o chains)  │         │
│  │ (6 wf)   │ │ (7 wf)   │ │ Graph    │ │                  │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘         │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐            │
│  │ PostgreSQL   │  │ Scoring      │  │ Config (.env)    │            │
│  │ (asyncpg)    │  │ Algorithms   │  │ Pydantic models  │            │
│  │ repository   │  │ (pure Python)│  │ Telegram bot     │            │
│  └──────────────┘  └──────────────┘  └──────────────────┘            │
└───────────────────────────────────────────────────────────────────────┘
```

### 5.2 Data Flow

#### User Question → Response

```
1. User types/speaks in the frontend
2. Frontend detects workflow via keywords (personal-ai-workflows.ts)
3. POST to the corresponding backend endpoint
4. Backend executes the appropriate LangGraph graph
5. Result is transformed (transformResponse) and rendered
6. Text is sent to TTS (OpenAI) → audio → Simli avatar
```

#### Voice Dashboard (WF-16)

```
"Hospital status"
  → detectDashboardType("executive")
  → POST /dashboard { command: "Hospital status" }
  → Router Graph:
      classify → "executive"
      execute → dashboard_insights + monitoring
      synthesize → builds structure + summarizes with GPT-4o
  → Returns full dashboard + ai_analysis
```

### 5.3 Workflow Mapping

| # | n8n Workflow | Backend | Type |
|---|-------------|---------|------|
| WF-01 | Chart summary | `clinical.py` → `chart_summary` | GPT-4o |
| WF-02 | Evolution summarization | `clinical.py` → `evolution_summary` | GPT-4o |
| WF-03 | Dashboard insights | `clinical.py` → `dashboard_insights` | GPT-4o |
| WF-04 | Queue prioritization | `scoring.py` → `queue_prioritization` | Algorithm |
| WF-05 | Denial prediction | `scoring.py` → `denial_prediction` | Algorithm |
| WF-06 | No-show prediction | `scoring.py` → `noshow_prediction` | Algorithm |
| WF-07 | Clinical documentation | `clinical.py` → `clinical_documentation` | GPT-4o |
| WF-08 | Regulatory copilot | `clinical.py` → `regulatory_copilot` | GPT-4o |
| WF-09 | Document review | `scoring.py` → `document_review` | Algorithm |
| WF-10 | Surgical scheduling | `scoring.py` → `surgical_scheduling` | Algorithm |
| WF-11 | Bottleneck detection | `scoring.py` → `bottlenecks` | Algorithm |
| WF-12 | Conversational copilot | `conversational.py` → LangGraph | GPT-4o |
| WF-13 | Post-discharge follow-up | `clinical.py` → `post_discharge_followup` | GPT-4o |
| WF-14 | KPI monitoring | `scoring.py` → `monitoring` | Algorithm |
| WF-16 | Voice dashboard | `router.py` → Router Graph | Orchestrator |

#### Dashboards (WF-16)

| Type | Workflows executed | Sections displayed |
|------|-------------------|-------------------|
| Executive | dashboard_insights, monitoring | status, alerts, units, insights, monitoring |
| Financial | denial_prediction, document_review | denials, documentation |
| Regulatory | queue_prioritization, regulatory_copilot | queue, analysis |
| Operational | bottlenecks, monitoring, surgical_scheduling | bottlenecks, units, surgical center, insights |
| Schedule | noshow_prediction, surgical_scheduling | no-show, surgical center |

### 5.4 Database

All agent data is queried from PostgreSQL via asyncpg, replacing the previous mock data.

**10 tables:**

| Table | Purpose | Used by |
|-------|---------|---------|
| `patients` | Patient registry | WF-01, WF-07, WF-13 |
| `clinical_evolutions` | Daily progress notes | WF-02, WF-07 |
| `regulatory_requests` | Authorization queue | WF-04 |
| `hospital_bills` | Accounts receivable | WF-05, WF-06 |
| `appointments` | Outpatient schedule | WF-09 |
| `hospital_units` | Occupancy monitoring | WF-14, dashboards |
| `surgical_rooms` | Room registry | WF-10 |
| `surgeries` | Scheduled surgeries | WF-10, WF-11 |
| `kpi_metrics` | Aggregated indicators | WF-03, dashboards |
| `chat_sessions` / `chat_messages` | Conversation memory | WF-12 |

**Seed data:** 50 patients with 282 clinical evolutions, 30 regulatory requests, 25 hospital bills, 40 appointments, 10 hospital units, 10 surgeries, 15 KPI metrics — all in English.

#### Schema

```sql
DO $$ BEGIN
    CREATE TYPE risk_level AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE priority_level AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE unit_status AS ENUM ('NORMAL', 'WARNING', 'CRITICAL');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE clinical_trend AS ENUM ('IMPROVING', 'STABLE', 'WORSENING');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS patients (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    age INTEGER NOT NULL,
    main_diagnosis VARCHAR NOT NULL,
    comorbidities TEXT[] DEFAULT '{}',
    allergies TEXT[] DEFAULT '{}',
    admission_date DATE NOT NULL,
    bed VARCHAR DEFAULT '',
    specialty VARCHAR DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clinical_evolutions (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    record_date DATE NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evolutions_patient_date
    ON clinical_evolutions(patient_id, record_date DESC);

CREATE TABLE IF NOT EXISTS regulatory_requests (
    id VARCHAR PRIMARY KEY,
    patient_name VARCHAR NOT NULL,
    age INTEGER NOT NULL,
    cid VARCHAR NOT NULL,
    procedure_name VARCHAR NOT NULL,
    wait_days INTEGER NOT NULL,
    clinical_risk risk_level NOT NULL,
    sla_days INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hospital_bills (
    id VARCHAR PRIMARY KEY,
    patient_name VARCHAR NOT NULL,
    insurance VARCHAR NOT NULL,
    procedure_name VARCHAR NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    has_medical_report BOOLEAN DEFAULT FALSE,
    has_surgical_report BOOLEAN DEFAULT FALSE,
    has_progress_notes BOOLEAN DEFAULT FALSE,
    has_opme_authorized BOOLEAN DEFAULT FALSE,
    icd_compatible BOOLEAN DEFAULT TRUE,
    historical_denial_rate DECIMAL(4,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_name VARCHAR NOT NULL,
    appointment_type VARCHAR NOT NULL,
    confirmed BOOLEAN DEFAULT FALSE,
    historical_miss_rate DECIMAL(4,2) DEFAULT 0,
    distance_km DECIMAL(6,2) DEFAULT 0,
    insurance_plan VARCHAR DEFAULT '',
    age INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hospital_units (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    occupancy_pct DECIMAL(5,1) NOT NULL,
    wait_time_min INTEGER NOT NULL,
    status unit_status NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS surgical_rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS surgeries (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES surgical_rooms(id) ON DELETE CASCADE,
    patient_name VARCHAR NOT NULL,
    procedure_name VARCHAR NOT NULL,
    specialty VARCHAR NOT NULL,
    is_urgent BOOLEAN DEFAULT FALSE,
    duration_min INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kpi_metrics (
    id SERIAL PRIMARY KEY,
    category VARCHAR NOT NULL,
    indicator VARCHAR NOT NULL,
    current_value DECIMAL(10,2),
    target_value DECIMAL(10,2),
    unit VARCHAR DEFAULT '',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    thread_id VARCHAR PRIMARY KEY,
    profile VARCHAR NOT NULL DEFAULT 'executive',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    thread_id VARCHAR NOT NULL REFERENCES chat_sessions(thread_id) ON DELETE CASCADE,
    role VARCHAR NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Seed Data

The database is populated by `src/db/seed.py` using the **Faker** library with `en_US` locale, generating all content in English:

| Data | Quantity | Details |
|------|----------|---------|
| Patients | 50 | Names, diagnoses (e.g. "Congestive Heart Failure"), comorbidities, allergies |
| Clinical evolutions | 282 | Distributed across patients with realistic daily progress notes in English (symptoms, procedures, medications) |
| Regulatory requests | 30 | Procedures, risk levels (`risk_level` enum), SLA deadlines |
| Hospital bills | 25 | Values (R$), document flags (medical report, surgical report, progress notes), denial rates |
| Appointments | 40 | Types (follow-up, exam, surgery), confirmation status, distance, historical miss rates |
| Hospital units | 10 | Occupancy %, wait times, status (`unit_status` enum: NORMAL, WARNING, CRITICAL) |
| Surgical rooms | 5 | Room names (e.g. "Surgery Room 1") |
| Surgeries | 10 | Scheduled with room assignment, specialty, duration, urgency flag |
| KPI metrics | 15 | Categories (financial, operational, clinical), indicators, current and target values |

The seed is **idempotent**: the `--skip-if-seeded` flag checks `SELECT COUNT(*) FROM patients` and skips if 10+ records exist. Run manually:

```bash
python -m src.db.seed --url postgresql://personalai:personalai_secret@localhost:5432/personalai --skip-if-seeded
```

### 5.5 Docker Setup

Three services orchestrated via Docker Compose:

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `db` | postgres:16-alpine | 5432 | PostgreSQL with healthcheck |
| `backend` | Python 3.12-slim | 8000 | FastAPI + LangGraph agents |
| `frontend` | Node 22-slim | 3000 | Vite dev server with HMR |

**Startup sequence:**
1. PostgreSQL healthcheck passes
2. Backend applies schema + seeds data (idempotent)
3. Backend starts uvicorn
4. Frontend starts (independent, depends on backend)

### 5.6 Deployment

#### Backend (Docker)

```bash
cd personal-ai-backend
docker compose up -d
```

For production, replace the development `command` with a production uvicorn run (without `--reload`).

#### Frontend (Cloudflare Workers)

```bash
cd personal-ai-frontend
npm run build
npx wrangler deploy   # config in wrangler.jsonc
```

### 5.7 Technical Notes

- **Windows:** `--reload` with uvicorn hangs (WatchFiles + multiprocessing pipe). Docker Linux containers handle it correctly.
- **Python 3.14:** Warning `Core Pydantic V1 functionality isn't compatible with Python 3.14` on startup — non-blocking.
- **Database:** Schema and seed are idempotent (safe to run multiple times).
- **Memory:** LangGraph checkpointer uses SQLite in Docker. For production, swap to PostgreSQL-backed checkpointing.
- **Avatar:** Simli requires valid `VITE_SIMLI_API_KEY` and `VITE_SIMLI_FACE_ID`. Without them, only TTS works.
- **CORS:** Allowed for `*` in development. Restrict in production.

### 5.8 n8n Migration Summary

| n8n | Python | Reason |
|-----|--------|--------|
| 6 GPT workflows (webhook → LLM → response) | `clinical.py` (LangGraph + chains) | Same logic, more control |
| 7 JS Code node workflows (scoring) | `scoring.py` + `scoring_tools.py` | Algorithms replicated in Python |
| 1 conversational workflow (GPT + memory) | `conversational.py` (LangGraph + checkpointer) | More robust memory and state |
| 1 orchestrator workflow (switch case) | `router.py` (Router Graph + LLM classify) | Smarter classification |

---

## 6. n8n vs Python Comparison

### 6.1 Comparison Table

| Aspect | n8n | Python + LangChain/LangGraph |
|--------|-----|-------------------------------|
| **Type** | Low-code visual automation platform | Programmatic framework with state graphs |
| **Language** | Visual + JavaScript (Code nodes) | Pure Python |
| **Learning curve** | Low — drag and drop nodes | Medium-high — requires Python, async, graph concepts |
| **Prototyping speed** | High — minutes to connect APIs | Medium — requires writing code, tests, endpoints |
| **Performance** | 200–500ms overhead per Code node (VM2 sandbox) | ~1–10ms for deterministic logic |
| **Infrastructure cost** | US$ 20–200/month (Cloud) or self-host (resources) | VPS only (~US$ 5–20/month) |
| **Development cost** | Lower initially — fast delivery | Higher initially — setup + code |
| **Automated tests** | Limited — manual workflow execution only | pytest, CI/CD, code coverage |
| **Versioning** | Export workflow JSON (hard to diff/review) | Standard git (diff, PR, blame, review) |
| **Ongoing maintenance** | Hard — changes break visual nodes | Controlled — typing + tests prevent regression |
| **Agent orchestration** | Limited — switch/case + chained webhooks | Native StateGraph with states, loops, decisions |
| **Conversational memory** | Manual — store in variables | Native checkpointing (SQLite, PostgreSQL) |
| **LLM switching** | Easy — swap the OpenAI node | Easy — swap provider in LangChain |
| **Debugging** | Open execution in browser, click nodes | breakpoint(), VS Code debugger, logs |
| **Scalability** | Vertical (plan defines limit) | Horizontal (multiple uvicorn workers + load balancer) |
| **Vendor lock-in** | High — logic, connectors, execution in n8n ecosystem | Low — Python runs anywhere |
| **Built-in connectors** | 400+ native integrations (Gmail, Slack, etc.) | Python standard library + requests for APIs |
| **Professional availability** | Niche — low-code developers | Massive — top bootcamps and universities teach Python |
| **Monitoring** | Native execution dashboard | Custom metrics (Prometheus, Grafana, logs) |

### 6.2 Pros and Cons

#### n8n

| ✅ Pros | ❌ Cons |
|---------|---------|
| Fast delivery for simple integrations | Hard to version (JSON diff is not readable) |
| Low technical barrier — non-dev teams can contribute | Manual testing only — does not scale |
| 400+ ready connectors | Low performance on JS nodes (VM2) |
| Visual — easy to understand the flow at a glance | Complex maintenance as workflows grow |
| Built-in monitoring | Loose JS code inside nodes — no standards |
| Great for prototyping and MVPs | Conditional orchestration becomes spaghetti of nodes |

#### Python + LangChain/LangGraph

| ✅ Pros | ❌ Cons |
|---------|---------|
| Git-versionable code (diff, PR, review) | Requires Python-skilled developers |
| Automated tests with pytest | Slower initial setup |
| No performance overhead (native code) | Steeper learning curve (LangGraph, async) |
| Complex orchestration with StateGraph | Must build monitoring from scratch |
| No vendor lock-in — runs on any infrastructure | Fewer ready connectors (need to implement) |
| Professional debugger (VS Code, breakpoints) | LangGraph documentation still evolving |
| Static typing with Pydantic | Python 3.14 has Pydantic v1 incompatibilities |
| Most widely used in AI/LLM space | |

### 6.3 Credentials and Security

| Aspect | n8n | Python + LangChain/LangGraph |
|--------|-----|-------------------------------|
| **Secret storage** | Encrypted internal vault (n8n database) | `.env` or external vault (HashiCorp Vault, AWS Secrets Manager) |
| **API key in code** | Stored in credential node — encrypted at rest | Stored in `.env` — outside source code |
| **Accidental secret leak** | Hard — UI does not expose value after saving | Easy — committing `.env` or hardcoded in code |
| **Access control** | Native RBAC (owner, member, —) | Application-level (FastAPI middleware, OAuth2, JWT) |
| **Audit trail** | Workflow execution logs | Git log + custom auth system |
| **Encryption in transit** | Depends on deployment (HTTPS via proxy) | Depends on deployment (HTTPS via proxy/TLS) |
| **Encryption at rest** | Secrets encrypted in n8n database | Secrets in plain text `.env` (needs external vault) |
| **Execution isolation** | Each execution is isolated (lightweight sandbox) | Each request is isolated (async Python) |
| **Input sanitization** | Automatic in HTTP/Webhook nodes | Manual — must validate with Pydantic |
| **Injection protection** | Good — nodes handle escaping automatically | Manual — SQL injection, command injection, etc. |
| **Key rotation** | Change in credential node — immediate effect | Change in `.env` + server restart |
| **Log exposure** | UI does not log credential values | Must be careful not to log secrets |
| **Certifications (SOC2, HIPAA)** | n8n Cloud has SOC2 | Team responsibility — implement from scratch |

#### n8n Security

| ✅ Pros | ❌ Cons |
|---------|---------|
| Native encrypted vault for secrets | Secrets stored in n8n database — if n8n is breached, everything is exposed |
| RBAC ready for teams | Limited granular permissions (only owner/member) |
| Built-in execution audit | No credential change audit beyond the log |
| UI hides credential value after saving | Depends on self-host for encryption in transit |
| Easy rotation — edit node and save | Rotation is not versioned — no changelog of who/when |

#### Python + FastAPI Security

| ✅ Pros | ❌ Cons |
|---------|---------|
| Secrets outside code (`.env`) — never in git if configured correctly | Easy to mistakenly commit `.env` to the repo |
| Can integrate professional vault (HashiCorp, AWS, Azure) | Vault setup is complex and costs infrastructure |
| Pydantic validation — strong typing prevents injection | Validation is manual — forgetting exposes the application |
| Git log audits every code change | Does not audit secret access in production |
| Full access control via middleware | Must implement from scratch (JWT, OAuth2, RBAC) |
| Runs behind any proxy (nginx, Cloudflare) | Full team responsibility for security |

#### Security Summary

| Situation | Lower risk in |
|-----------|---------------|
| Accidental secret leak (commit) | n8n — UI does not expose saved value |
| Code and change audit | Python — full git history |
| Granular access control | Python — custom implementation |
| Quick setup with basic security | n8n — native vault and RBAC |
| Compliance (HIPAA, SOC2, LGPD) | Python — full control to certify |
| Small team without dedicated devops | n8n — less security responsibility |

> The main difference: in n8n security comes "built-in" but you don't control the details. In Python you have full control but need to implement (or pay for) each layer.

### 6.4 When to Use Each

| Scenario | Recommendation |
|----------|---------------|
| Connect Slack + Gmail + Sheets quickly | n8n |
| Workflow with < 5 steps and no complex logic | n8n |
| Non-technical team needs to create/modify flows | n8n |
| Proof of concept / MVP in days | n8n |
| **Scoring algorithms and business rules** | **Python** |
| **Chat with memory and state (agents)** | **Python + LangGraph** |
| **Automated tests required** | **Python** |
| **Engineering team maintaining the code** | **Python** |
| **Multiple LLMs and frequent provider switching** | **Python + LangChain** |
| **Horizontal scaling in production** | **Python + FastAPI** |

### 6.5 Real Project Numbers

| Metric | n8n (before) | Python (after) |
|--------|-------------|----------------|
| Workflows | 14 | 14 (rewritten) |
| Automated tests | 0 | 4 (scoring) + expanding |
| Backend lines of code | ~30 visual nodes + ~600 lines JS | ~800 lines Python |
| Average scoring time | ~300ms (with n8n overhead) | ~5ms |
| External dependencies | n8n Cloud + Docker | Python + pip |

---

## 7. Quick Start

```bash
# Start everything with Docker
cd personal-ai-backend
echo "OPENAI_API_KEY=sk-..." > .env
docker compose up -d

# Backend:  http://localhost:8000
# Frontend: http://localhost:3000
# Swagger:  http://localhost:8000/docs
```
