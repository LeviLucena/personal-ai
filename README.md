# Salux Health AI

Plataforma de inteligência artificial para gestão hospitalar.

## Repositório

```
salux-ai-backend/   → API Python (FastAPI + LangChain/LangGraph)
salux-ai-frontend/  → SPA React (TanStack Start + Tailwind v4)
```

## Documentação

| Documento | Descrição |
|-----------|-----------|
| `salux-ai-backend/README.md` | Setup e endpoints do backend |
| `salux-ai-frontend/README.md` | Setup e componentes do frontend |
| `salux-ai-backend/SALUX.md` | Documentação unificada (arquitetura, fluxo, deploy, migração) |
| `salux-ai-backend/N8N_VS_PYTHON.md` | Comparativo n8n vs Python + LangChain/LangGraph |

## Quick start

```bash
# Backend
cd salux-ai-backend
cp .env.example .env  # edite OPENAI_API_KEY
pip install -e .
start.bat

# Frontend (outro terminal)
cd salux-ai-frontend
npm install
npm run dev
```

## Stack

- **Backend:** Python 3.12+ · FastAPI · LangGraph · OpenAI GPT-4o
- **Frontend:** React 19 · TanStack Start · Tailwind CSS v4 · shadcn/ui
- **Avatar:** Simli · TTS: OpenAI · STT: Web Speech API
