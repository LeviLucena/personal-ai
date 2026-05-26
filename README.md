# Personal AI

![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white) ![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white) ![OpenAI](https://img.shields.io/badge/OpenAI_GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white) ![asyncpg](https://img.shields.io/badge/asyncpg-336791?style=for-the-badge&logo=postgresql&logoColor=white) ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![Telegram Bot](https://img.shields.io/badge/Telegram_Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white) ![React](https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black) ![TanStack Start](https://img.shields.io/badge/TanStack_Start-FF4154?style=for-the-badge&logo=tanstack&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript_5-3178C6?style=for-the-badge&logo=typescript&logoColor=white) ![Vite](https://img.shields.io/badge/Vite_7-646CFF?style=for-the-badge&logo=vite&logoColor=white) ![Cloudflare](https://img.shields.io/badge/Cloudflare_Workers-F38020?style=for-the-badge&logo=cloudflare&logoColor=white) ![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS_v4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white) ![Radix UI](https://img.shields.io/badge/Radix_UI-161618?style=for-the-badge&logo=radixui&logoColor=white) ![Framer Motion](https://img.shields.io/badge/Framer_Motion-0055FF?style=for-the-badge&logo=framer&logoColor=white) ![Simli](https://img.shields.io/badge/Simli_Avatar-635BFF?style=for-the-badge&logo=heygen&logoColor=white) ![Zod](https://img.shields.io/badge/Zod-3E67B1?style=for-the-badge&logo=zod&logoColor=white) ![React Hook Form](https://img.shields.io/badge/React_Hook_Form-EC5990?style=for-the-badge&logo=reacthookform&logoColor=white) ![Recharts](https://img.shields.io/badge/Recharts-22B5BF?style=for-the-badge&logo=recharts&logoColor=white)

AI-powered hospital management platform. Replaces 14 n8n workflows with Python agents (LangChain/LangGraph + GPT-4o) and a modern React frontend with voice interaction and digital avatar.

## Repositories

```
personal-ai-backend/   → Python API (FastAPI + LangChain/LangGraph + PostgreSQL)
personal-ai-frontend/  → React SPA (TanStack Start + Tailwind v4)
```

## Documentation

| File | Description |
|------|-------------|
| `personal-ai-backend/README.md` | Backend setup, endpoints, and workflows |
| `personal-ai-frontend/README.md` | Frontend setup, components, and scripts |
| `ARCHITECTURE.md` | Unified architecture, flow, deployment, migration docs |
| `personal-ai-backend/N8N_VS_PYTHON.md` | n8n vs Python + LangChain/LangGraph comparison |

## System Flow

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

> **SVG export:** Copy the Mermaid block above to [mermaid.live](https://mermaid.live) or use the CLI: `mmdc -i README.md -o architecture.svg -t dark -b transparent`

## Quick Start
cd personal-ai-backend
echo "OPENAI_API_KEY=sk-..." > .env
docker compose up -d

# Backend:  http://localhost:8000
# Frontend: http://localhost:3000
# Swagger:  http://localhost:8000/docs
```
