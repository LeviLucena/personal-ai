# Salux Health AI — Documentação Unificada

Plataforma de inteligência artificial para gestão hospitalar. Backend agentivo em Python (LangChain/LangGraph + GPT-4o) + frontend conversacional (React/TanStack Start + Tailwind).

---

## 1. Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React SPA)                        │
│  TanStack Start · Tailwind v4 · shadcn/ui · Framer Motion          │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │   Orb    │  │  Input   │  │  Avatar       │  │  Response      │  │
│  │ (estado) │  │ (voz+txt)│  │  Simli (TTS)  │  │  Renderer      │  │
│  └──────────┘  └──────────┘  └──────────────┘  └────────────────┘  │
│                        │ HTTP (fetch)                               │
└────────────────────────┼────────────────────────────────────────────┘
                         │ POST /workflow · /chat · /dashboard
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI + LangGraph)                  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Router Graph (WF-16)                      │   │
│  │  classifica → [sub-graphs] → sintetiza resposta             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                    │ dispatches to                                  │
│        ┌───────────┼───────────┬───────────────────┐               │
│        ▼           ▼           ▼                   ▼               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐       │
│  │ Clinical │ │ Scoring  │ │ Conversa-│ │ LLM Tools        │       │
│  │ Graph    │ │ Graph    │ │ tional   │ │ (GPT-4o chains)  │       │
│  │ (6 wf)   │ │ (7 wf)   │ │ Graph    │ │                  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘       │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐          │
│  │ Mock Data    │  │ Scoring      │  │ Config (.env)    │          │
│  │ (PowerBuilder│  │ Algorithms   │  │ Pydantic models  │          │
│  │  eventual)   │  │ (Python JS)  │  │ Telegram bot     │          │
│  └──────────────┘  └──────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Fluxo de Dados

### Pergunta do usuário → Resposta

```
1. Usuário digita/fala no frontend
2. Frontend detecta workflow por keywords (salux-workflows.ts)
3. POST para o endpoint correspondente no backend
4. Backend executa o grafo LangGraph apropriado
5. Resultado é transformado (transformResponse) e renderizado
6. Texto é enviado ao TTS (OpenAI) → áudio → avatar Simli
```

### Dashboard por voz (WF-16)

```
"Status do hospital"
  → detectDashboardType("executivo")
  → POST /dashboard { comando: "Status do hospital" }
  → Router Graph:
      classify → "executivo"
      execute → insights_dashboard + monitoramento
      synthesize → monta estrutura + resume com GPT-4o
  → Retorna dashboard completo + analise_ia
```

---

## 3. Workflows

### Mapeamento Original → Implementação Atual

| # | Workflow n8n | Backend | Tipo |
|---|-------------|---------|------|
| WF-01 | Resumo de prontuário | `clinical.py` → `resumo_prontuario` | GPT-4o |
| WF-02 | Sumarização de evolução | `clinical.py` → `sumarizacao_evolucao` | GPT-4o |
| WF-03 | Insights de dashboard | `clinical.py` → `insights_dashboard` | GPT-4o |
| WF-04 | Priorização de filas | `scoring.py` → `priorizacao_filas` | Algoritmo |
| WF-05 | Predição de glosa | `scoring.py` → `predicao_glosa` | Algoritmo |
| WF-06 | Predição de no-show | `scoring.py` → `predicao_noshow` | Algoritmo |
| WF-07 | Documentação clínica | `clinical.py` → `documentacao_clinica` | GPT-4o |
| WF-08 | Copiloto regulatório | `clinical.py` → `copilot_regulatorio` | GPT-4o |
| WF-09 | Conferência documental | `scoring.py` → `conferencia_documental` | Algoritmo |
| WF-10 | Agendamento cirúrgico | `scoring.py` → `agendamento_cirurgico` | Algoritmo |
| WF-11 | Gargalos operacionais | `scoring.py` → `gargalos` | Algoritmo |
| WF-12 | Copiloto conversacional | `conversational.py` → LangGraph | GPT-4o |
| WF-13 | Follow-up pós-alta | `clinical.py` → `followup_pos_alta` | GPT-4o |
| WF-14 | Monitoramento | `scoring.py` → `monitoramento` | Algoritmo |
| WF-16 | Dashboard por voz | `router.py` → Router Graph | Orquestrador |

### Dashboards (WF-16)

| Tipo | Workflows executados | Seções exibidas |
|------|---------------------|-----------------|
| Executivo | insights_dashboard, monitoramento | status, alertas, unidades, insights, monitoramento |
| Financeiro | predicao_glosa, conferencia_documental | glosas, documentação |
| Regulatório | priorizacao_filas, copilot_regulatorio | fila, análise |
| Operacional | gargalos, monitoramento, agendamento_cirurgico | gargalos, unidades, centro cirúrgico, insights |
| Agenda | predicao_noshow, agendamento_cirurgico | no-show, centro cirúrgico |

---

## 4. Endpoints da API

Base: `http://localhost:8000`

### `GET /health`
Health check.
```json
{ "status": "ok" }
```

### `POST /workflow`
Executa um workflow específico.
```json
{
  "workflow": "documentacao_clinica",
  "input": { "texto_clinico": "Paciente João..." }
}
```

### `POST /chat`
Copiloto conversacional com memória.
```json
{
  "message": "Qual a taxa de ocupação?",
  "perfil": "executivo",
  "thread_id": "abc123"
}
```

### `POST /dashboard`
Dashboard por voz. Classifica, executa e sintetiza.
```json
{
  "comando": "Status do hospital"
}
```

### `GET /workflows`
Lista todos os workflows e dashboards disponíveis.

---

## 5. Setup Completo

### Pré-requisitos
- Python 3.12+ (Windows Store Python recomendado no Windows)
- Node.js 20+
- Chave de API OpenAI (GPT-4o)

### Backend

```bash
cd salux-ai-backend
cp .env.example .env
# Edite OPENAI_API_KEY no .env

pip install -e .
# ou: pip install -r requirements.txt

start.bat
# Servidor em http://localhost:8000
```

### Frontend

```bash
cd salux-ai-frontend
# Edite .env se necessário

npm install
npm run dev
# Dev server em http://localhost:8080
```

---

## 6. Variáveis de Ambiente

### Backend (.env)

| Variável | Descrição | Default |
|----------|-----------|---------|
| `OPENAI_API_KEY` | Chave da OpenAI | — |
| `OPENAI_MODEL` | Modelo OpenAI | `gpt-4o` |
| `HOST` | Host do servidor | `0.0.0.0` |
| `PORT` | Porta do servidor | `8000` |
| `TELEGRAM_BOT_TOKEN` | Token do bot Telegram (opcional) | — |
| `DATABASE_URL` | URL do banco de dados (futuro) | — |

### Frontend (.env)

| Variável | Descrição | Default |
|----------|-----------|---------|
| `VITE_API_BASE_URL` | URL do backend | `http://localhost:8000` |
| `VITE_SIMLI_API_KEY` | Chave da API Simli | — |
| `VITE_SIMLI_FACE_ID` | ID do avatar Simli | — |
| `VITE_OPENAI_API_KEY` | Chave OpenAI (TTS) | — |

---

## 7. Testes

```bash
# Backend
cd salux-ai-backend
pytest tests/

# Frontend
cd salux-ai-frontend
npm run build    # verifica erros de compilação
npm run lint     # ESLint
```

---

## 8. Deploy

### Backend (produção)

```bash
# Docker (futuro)
docker build -t salux-ai-backend .
docker run -p 8000:8000 --env-file .env salux-ai-backend

# Direto com uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Frontend (Cloudflare Workers)

```bash
cd salux-ai-frontend
npm run build
# Deploy via wrangler (config em wrangler.jsonc)
npx wrangler deploy
```

---

## 9. Observações Técnicas

- **Windows:** `--reload` não funciona com uvicorn no Windows (WatchFiles + pipe multiprocessing). Use `start.bat` sem `--reload`.
- **Python 3.14:** Aviso `Core Pydantic V1` no startup — não bloqueante.
- **Dados mock:** Substituir `mock_data.py` por chamadas HTTP reais ao PowerBuilder quando disponível.
- **Memória:** LangGraph checkpointer usa SQLite (em memória). Trocar por PostgreSQL em produção.
- **Avatar:** Simli requer `VITE_SIMLI_API_KEY` e `VITE_SIMLI_FACE_ID` válidos. Sem eles, apenas TTS funciona.
- **CORS:** Liberado para `*` em desenvolvimento. Restringir em produção.

---

## 10. Migração do n8n

Este projeto substitui 14 workflows n8n por uma arquitetura agentiva em Python:

| n8n | Python | Motivo |
|-----|--------|--------|
| 6 workflows com GPT (webhook → LLM → response) | `clinical.py` (LangGraph + chains) | Mesma lógica, mais controle |
| 7 workflows com JS Code nodes (scoring) | `scoring.py` + `scoring_tools.py` | Algoritmos replicados em Python |
| 1 workflow conversacional (GPT + memória) | `conversational.py` (LangGraph + checkpointer) | Memória e estados mais robustos |
| 1 workflow orquestrador (switch case) | `router.py` (Router Graph + LLM classify) | Classificação mais inteligente |

**Benefícios:** stack unificado (Python + TypeScript), sem dependência de n8n, testes automatizados, versionamento com git, deploy padrão.
