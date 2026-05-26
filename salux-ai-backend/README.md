# Salux Health AI — Backend

API inteligente do hospital Salux. Substitui 14 workflows n8n por agentes Python com LangChain/LangGraph + GPT-4o.

## Stack

- **Framework:** FastAPI
- **Orquestração:** LangGraph (StateGraph)
- **LLM:** OpenAI GPT-4o via `langchain-openai`
- **Modelagem:** Pydantic v2
- **Bot:** Telegram via aiogram (opcional)

## Estrutura

```
src/
  main.py              # FastAPI entrypoint (5 endpoints)
  config.py            # Config via pydantic-settings + .env
  agents/
    router.py          # WF-16: classifica intenção, executa sub-grafos, sintetiza
    clinical.py        # WF-01..03,07,08,13: chains clínicas com GPT-4o
    scoring.py         # WF-04..06,09..11,14: algoritmos determinísticos de scoring
    conversational.py  # WF-12: chat com LangGraph + checkpointer (memória)
  tools/
    llm_tools.py       # Prompts e chains do GPT-4o (6 chains)
    scoring_tools.py   # Algoritmos de scoring migrados do n8n JS
    mock_data.py       # Dados mock espelhando os JSONs originais do n8n
  models/              # Schemas Pydantic (clinical, financial, operational)
  channels/
    telegram.py        # Bot Telegram (aiogram, desabilitado sem token)
tests/
  test_scoring.py      # Testes unitários dos algoritmos de scoring
```

## Endpoints

| Método | Rota           | Descrição                                      |
|--------|----------------|------------------------------------------------|
| GET    | `/health`      | Health check                                   |
| POST   | `/workflow`    | Executa workflow clínico, scoring ou chat      |
| POST   | `/chat`        | Copiloto conversacional (com memória)          |
| POST   | `/dashboard`   | Dashboard por voz (classifica + executa + resume) |
| GET    | `/workflows`   | Lista workflows e dashboards disponíveis       |

## Workflows

**Clínicos (GPT-4o):** `resumo_prontuario`, `sumarizacao_evolucao`, `insights_dashboard`, `documentacao_clinica`, `copilot_regulatorio`, `followup_pos_alta`

**Scoring (determinístico):** `priorizacao_filas`, `predicao_glosa`, `predicao_noshow`, `conferencia_documental`, `agendamento_cirurgico`, `gargalos`, `monitoramento`

**Dashboard:** `executivo`, `financeiro`, `regulatorio`, `operacional`, `agenda`

## Setup

```bash
git clone <repo>
cd salux-ai-backend

# Crie o .env (veja .env.example)
cp .env.example .env
# Edite OPENAI_API_KEY

# Instale dependências
pip install -e .

# Inicie o servidor
start.bat
# ou: uvicorn src.main:app --host 127.0.0.1 --port 8000
```

## Testes

```bash
pytest tests/
```

## Observações

- `--reload` não funciona no Windows (WatchFiles + multiprocessing pipe). Use sem `--reload`.
- Todos os dados são mockados. Substituir `mock_data.py` por chamadas HTTP reais ao PowerBuilder quando disponível.
- Python 3.12+ necessário. Testado com Windows Store Python 3.14.
