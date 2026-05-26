from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.agents.clinical import build_clinical_graph
from src.agents.scoring import build_scoring_graph
from src.agents.conversational import build_conversational_graph
from src.agents.router import build_router_graph, DASHBOARD_MAP
from src.config import settings

app = FastAPI(title="Salux Health AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WorkflowRequest(BaseModel):
    workflow: str
    input: dict = {}


class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"
    perfil: str = "executivo"


class DashboardRequest(BaseModel):
    comando: str


CLINICAL_WFS = {
    "resumo_prontuario", "sumarizacao_evolucao", "insights_dashboard",
    "documentacao_clinica", "copilot_regulatorio", "followup_pos_alta",
}

SCORING_WFS = {
    "priorizacao_filas", "predicao_glosa", "predicao_noshow",
    "conferencia_documental", "agendamento_cirurgico", "gargalos", "monitoramento",
}


@app.post("/workflow")
async def run_workflow(req: WorkflowRequest):
    if req.workflow in CLINICAL_WFS:
        graph = build_clinical_graph()
        result = await graph.ainvoke({
            "input": req.input,
            "workflow": req.workflow,
            "output": {},
        })
        return result.get("output", {})

    if req.workflow in SCORING_WFS:
        graph = build_scoring_graph()
        result = await graph.ainvoke({
            "input": req.input,
            "workflow": req.workflow,
            "output": {},
        })
        return result.get("output", {})

    if req.workflow == "conversacional":
        graph = build_conversational_graph()
        config = {"configurable": {"thread_id": req.input.get("thread_id", "default")}}
        result = await graph.ainvoke({
            "messages": [("user", req.input.get("message", ""))]
        }, config)
        return {"resposta": result["messages"][-1].content}

    raise HTTPException(status_code=400, detail=f"Workflow desconhecido: {req.workflow}")


@app.get("/workflows")
async def list_workflows():
    return {
        "clinical": sorted(CLINICAL_WFS),
        "scoring": sorted(SCORING_WFS),
        "dashboards": {k: v["description"] for k, v in DASHBOARD_MAP.items()},
    }


@app.post("/dashboard")
async def dashboard_voz(req: DashboardRequest):
    graph = build_router_graph()
    result = await graph.ainvoke({
        "input": {"comando": req.comando},
        "dashboard_type": "",
        "sub_results": {},
        "final_output": {},
    })
    return result.get("final_output", {})


@app.post("/chat")
async def chat(req: ChatRequest):
    graph = build_conversational_graph()
    config = {"configurable": {"thread_id": req.thread_id}}
    result = await graph.ainvoke({
        "messages": [
            ("user", f"[Perfil: {req.perfil}] {req.message}"),
        ]
    }, config)
    return {
        "resposta": result["messages"][-1].content,
        "thread_id": req.thread_id,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
