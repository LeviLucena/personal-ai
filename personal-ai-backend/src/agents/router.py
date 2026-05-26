from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict, Any
from src.config import settings
from src.agents.clinical import build_clinical_graph
from src.agents.scoring import build_scoring_graph
from src.agents.conversational import build_conversational_graph


class RouterState(TypedDict):
    input: dict
    dashboard_type: str
    sub_results: dict
    final_output: dict


router_prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the user command into one of the following dashboard types: "
     "executivo, financeiro, regulatorio, operacional, agenda. "
     "Reply ONLY with the type name, no explanation."),
    ("human", "{comando}"),
])

DASHBOARD_MAP = {
    "executivo": {
        "workflows": ["insights_dashboard", "monitoramento"],
        "description": "Hospital status, general summary",
    },
    "financeiro": {
        "workflows": ["predicao_glosa", "conferencia_documental"],
        "description": "Financial risk, deductions, billing",
    },
    "regulatorio": {
        "workflows": ["priorizacao_filas", "copilot_regulatorio"],
        "description": "Regulatory queue, authorization",
    },
    "operacional": {
        "workflows": ["gargalos", "monitoramento", "agendamento_cirurgico"],
        "description": "Bottlenecks, surgical center, capacity",
    },
    "agenda": {
        "workflows": ["predicao_noshow", "agendamento_cirurgico"],
        "description": "Scheduling, appointments, no-show",
    },
}

llm = ChatOpenAI(model=settings.openai_model, temperature=0)


async def classify_command(state: RouterState) -> dict:
    comando = state["input"].get("comando", "")
    result = await router_prompt.ainvoke({"comando": comando})
    response = (await llm.ainvoke(result)).content.strip().lower()

    for key in DASHBOARD_MAP:
        if key in response:
            return {"dashboard_type": key}

    return {"dashboard_type": "executivo"}


async def execute_dashboard(state: RouterState) -> dict:
    dashboard = state["dashboard_type"]
    wf_list = DASHBOARD_MAP.get(dashboard, DASHBOARD_MAP["executivo"])["workflows"]
    sub_results = {}

    clinical_graph = build_clinical_graph()
    scoring_graph = build_scoring_graph()

    for wf in wf_list:
        if wf in ["resumo_prontuario", "sumarizacao_evolucao", "insights_dashboard",
                    "documentacao_clinica", "copilot_regulatorio", "followup_pos_alta"]:
            result = await clinical_graph.ainvoke({
                "input": state["input"],
                "workflow": wf,
                "output": {},
            })
            sub_results[wf] = result.get("output", {})

        elif wf in ["priorizacao_filas", "predicao_glosa", "predicao_noshow",
                     "conferencia_documental", "agendamento_cirurgico", "gargalos", "monitoramento"]:
            result = await scoring_graph.ainvoke({
                "input": state["input"],
                "workflow": wf,
                "output": {},
            })
            sub_results[wf] = result.get("output", {})

    return {"sub_results": sub_results}


async def synthesize_response(state: RouterState) -> dict:
    from src.agents.conversational import build_conversational_graph
    sub = state["sub_results"]

    tipo = state["dashboard_type"]
    merged: dict = {"dashboard": tipo.upper()}

    mon = sub.get("monitoramento", {})

    unidades = mon.get("unidades", [])
    status_list = [u["status"] for u in unidades if u.get("status") == "CRITICAL"]
    merged["status_operacional"] = "CRITICAL" if status_list else "NORMAL"
    merged["alertas_ativos"] = len(status_list)
    merged["unidades_criticas"] = [
        u["nome"] for u in unidades if u.get("status") == "CRITICAL"
    ]

    garg = sub.get("gargalos", {})
    if garg:
        merged["gargalos"] = {
            "previsoes": garg.get("previsoes", {}),
            "top_alertas": [{"mensagem": a, "severidade": "CRITICAL"} for a in garg.get("acoes", [])],
        }

    if mon:
        merged["monitoramento"] = {"unidades": unidades}

    gli = sub.get("predicao_glosa", {})
    if gli:
        contas = gli.get("contas_analisadas", [])
        merged["glosas"] = {
            "criticas": sum(1 for c in contas if c.get("classificacao") == "CRITICAL"),
            "total_contas": len(contas),
            "valor_total_em_risco": f"R$ {gli.get('valor_total_em_risco', 0):,.2f}",
            "top_risco": [
                {"conta": c.get("id", ""), "score": c.get("score_risco_glosa", 0), "acao": c.get("acao_recomendada", "")}
                for c in contas[:6]
            ],
        }

    doc = sub.get("conferencia_documental", {})
    if doc:
        merged["documentacao"] = {
            "score_completude": doc.get("score_completude", 0),
            "status_faturamento": "APPROVED" if doc.get("score_completude", 0) >= 80 else "PENDING",
        }

    fila = sub.get("priorizacao_filas", {})
    if fila:
        fp = fila.get("fila_priorizada", [])
        merged["fila"] = {
            "total": len(fp),
            "criticas": sum(1 for f in fp if f.get("prioridade") in ("CRITICAL", "HIGH")),
            "sla_estourado": sum(1 for f in fp if f.get("sla_estourado")),
            "top_prioritarios": [
                {"paciente": f.get("solicitacao", {}).get("paciente", ""),
                 "score": f.get("score_total", 0),
                 "prioridade": f.get("prioridade", ""),
                 "cid": f.get("solicitacao", {}).get("cid", "")}
                for f in fp[:6]
            ],
        }

    noshow = sub.get("predicao_noshow", {})
    if noshow:
        ag = noshow.get("agenda_analisada", [])
        merged["no_show"] = {
            "alto_risco": sum(1 for a in ag if a.get("risco") == "HIGH"),
            "total_consultas": len(ag),
            "acoes_urgentes": [
                {"paciente": a.get("paciente", ""),
                 "probabilidade": a.get("probabilidade_noshow", 0),
                 "acao": a.get("acao_recomendada", "")}
                for a in ag[:6]
            ],
        }

    cc = sub.get("agendamento_cirurgico", {})
    if cc:
        salas = cc.get("salas", [])
        merged["centro_cirurgico"] = {
            "cirurgias_alocadas": sum(len(s.get("cirurgias", [])) for s in salas),
            "nao_alocadas": 0,
        }

    conv_graph = build_conversational_graph()
    summary_input = "\n".join(f"{k}: {v}" for k, v in sub.items())
    result = await conv_graph.ainvoke({
        "messages": [
            ("user", f"Summarize the following {tipo} dashboard in up to 3 short sentences:\n{summary_input}")
        ]
    })

    merged["analise_ia"] = result["messages"][-1].content

    return {"final_output": merged}


def build_router_graph() -> StateGraph:
    builder = StateGraph(RouterState)

    builder.add_node("classify", classify_command)
    builder.add_node("execute", execute_dashboard)
    builder.add_node("synthesize", synthesize_response)

    builder.add_edge(START, "classify")
    builder.add_edge("classify", "execute")
    builder.add_edge("execute", "synthesize")
    builder.add_edge("synthesize", END)

    return builder.compile()
