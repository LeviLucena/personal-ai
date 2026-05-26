# Personal AI — Architecture

AI-powered hospital management platform. Agentive Python backend (LangChain/LangGraph + GPT-4o) + conversational React frontend (TanStack Start + Tailwind) + PostgreSQL + Docker.

---

## 1. Overall Architecture

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

---

## 2. Data Flow

### User Question → Response

```
1. User types/speaks in the frontend
2. Frontend detects workflow via keywords (personal-ai-workflows.ts)
3. POST to the corresponding backend endpoint
4. Backend executes the appropriate LangGraph graph
5. Result is transformed (transformResponse) and rendered
6. Text is sent to TTS (OpenAI) → audio → Simli avatar
```

### Voice Dashboard (WF-16)

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

---

## 3. Workflows

### Original n8n → Current Implementation

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

### Dashboards (WF-16)

| Type | Workflows executed | Sections displayed |
|------|-------------------|-------------------|
| Executive | dashboard_insights, monitoring | status, alerts, units, insights, monitoring |
| Financial | denial_prediction, document_review | denials, documentation |
| Regulatory | queue_prioritization, regulatory_copilot | queue, analysis |
| Operational | bottlenecks, monitoring, surgical_scheduling | bottlenecks, units, surgical center, insights |
| Schedule | noshow_prediction, surgical_scheduling | no-show, surgical center |

---

## 4. API Endpoints

Base: `http://localhost:8000`

### `GET /health`
Health check.
```json
{ "status": "ok" }
```

### `POST /workflow`
Execute a specific workflow.
```json
{
  "workflow": "clinical_documentation",
  "input": { "clinical_notes": "Patient John..." }
}
```

### `POST /chat`
Conversational copilot with memory.
```json
{
  "message": "What is the occupancy rate?",
  "profile": "executive",
  "thread_id": "abc123"
}
```

### `POST /dashboard`
Voice dashboard. Classifies, executes, and synthesizes.
```json
{
  "command": "Hospital status"
}
```

### `GET /workflows`
List all available workflows and dashboards.

---

## 5. Database (PostgreSQL)

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

### Schema

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

### Seed Data

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

---

## 6. Docker Setup

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

---

## 7. Setup

### Docker (recommended)

```bash
cd personal-ai-backend
echo "OPENAI_API_KEY=sk-..." > .env
docker compose up -d
```

### Manual

```bash
# Backend
cd personal-ai-backend
pip install -e .
uvicorn src.main:app --host 127.0.0.1 --port 8000

# Frontend (separate terminal)
cd personal-ai-frontend
npm install
npm run dev
```

---

## 8. Environment Variables

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL DSN | `postgresql://personalai:personalai_secret@localhost:5432/personalai` |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `OPENAI_MODEL` | Model name | `gpt-4o` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (optional) | — |

### Frontend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend URL | `http://localhost:8000` |
| `VITE_SIMLI_API_KEY` | Simli API key | — |
| `VITE_SIMLI_FACE_ID` | Simli avatar ID | — |
| `VITE_OPENAI_API_KEY` | OpenAI key (TTS) | — |

---

## 9. Testing

```bash
# Backend
cd personal-ai-backend
pytest tests/

# Frontend
cd personal-ai-frontend
npm run build    # check for compilation errors
npm run lint     # ESLint
```

---

## 10. Deployment

### Backend (Docker)

```bash
cd personal-ai-backend
docker compose up -d
```

For production, replace the development `command` with a production uvicorn run (without `--reload`).

### Frontend (Cloudflare Workers)

```bash
cd personal-ai-frontend
npm run build
npx wrangler deploy   # config in wrangler.jsonc
```

---

## 11. Technical Notes

- **Windows:** `--reload` with uvicorn hangs (WatchFiles + multiprocessing pipe). Docker Linux containers handle it correctly.
- **Python 3.14:** Warning `Core Pydantic V1 functionality isn't compatible with Python 3.14` on startup — non-blocking.
- **Database:** Schema and seed are idempotent (safe to run multiple times).
- **Memory:** LangGraph checkpointer uses SQLite in Docker. For production, swap to PostgreSQL-backed checkpointing.
- **Avatar:** Simli requires valid `VITE_SIMLI_API_KEY` and `VITE_SIMLI_FACE_ID`. Without them, only TTS works.
- **CORS:** Allowed for `*` in development. Restrict in production.

---

## 12. n8n Migration

This project replaces 14 n8n workflows with an agentive Python architecture:

| n8n | Python | Reason |
|-----|--------|--------|
| 6 GPT workflows (webhook → LLM → response) | `clinical.py` (LangGraph + chains) | Same logic, more control |
| 7 JS Code node workflows (scoring) | `scoring.py` + `scoring_tools.py` | Algorithms replicated in Python |
| 1 conversational workflow (GPT + memory) | `conversational.py` (LangGraph + checkpointer) | More robust memory and state |
| 1 orchestrator workflow (switch case) | `router.py` (Router Graph + LLM classify) | Smarter classification |

**Benefits:** unified stack (Python + TypeScript), no n8n dependency, automated tests, git versioning, standard deployment.
