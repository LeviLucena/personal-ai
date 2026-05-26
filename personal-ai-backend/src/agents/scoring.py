from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from src.tools.scoring_tools import priorizacao_fila, predicao_glosa, predicao_noshow
from src.db import (
    get_regulatory_requests, get_hospital_bills,
    get_appointments, get_hospital_units,
)


class ScoringState(TypedDict):
    workflow: str
    input: dict
    output: dict


async def run_priorizacao(state: ScoringState) -> dict:
    fila = await get_regulatory_requests()
    resultados = [priorizacao_fila(s) for s in fila]
    resultados.sort(key=lambda x: x.score_total, reverse=True)
    return {"output": {"fila_priorizada": [r.model_dump() for r in resultados]}}


async def run_predicao_glosa(state: ScoringState) -> dict:
    contas = await get_hospital_bills()
    resultados = [predicao_glosa(c) for c in contas]
    resultados.sort(key=lambda x: x["score_risco_glosa"], reverse=True)
    total_risco = sum(r["valor_em_risco"] for r in resultados)
    return {"output": {"contas_analisadas": resultados, "valor_total_em_risco": round(total_risco, 2)}}


async def run_predicao_noshow(state: ScoringState) -> dict:
    consultas = await get_appointments()
    resultados = [predicao_noshow(c) for c in consultas]
    resultados.sort(key=lambda x: x["probabilidade_noshow"], reverse=True)
    return {"output": {"agenda_analisada": resultados}}


async def run_conferencia_documental(state: ScoringState) -> dict:
    contas = await get_hospital_bills()
    score_total = sum(
        10 for c in contas
        if c["tem_laudo"] and c["tem_relatorio_cirurgico"] and c["tem_evolucoes"]
    )
    documentos_ok = sum(
        1 for c in contas
        if c["tem_laudo"] and c["tem_relatorio_cirurgico"]
    )
    return {
        "output": {
            "score_completude": round(score_total / len(contas) * 10, 1) if contas else 0,
            "documentos_ok": documentos_ok,
            "total_contas": len(contas),
        }
    }


async def run_agendamento_cirurgico(state: ScoringState) -> dict:
    from src.db import get_surgical_data
    surg = await get_surgical_data()
    return {"output": surg}


async def run_gargalos(state: ScoringState) -> dict:
    return {
        "output": {
            "previsoes": {
                "pacientes_espera": 28,
                "tempo_medio_espera_min": 69,
                "ocupacao_leitos_pct": 100,
            },
            "status_geral": "CRITICAL",
            "acoes": [
                "Call additional physician",
                "Prioritize Manchester triage",
                "Transfer stable patients to ward",
            ],
        }
    }


async def run_monitoramento(state: ScoringState) -> dict:
    unidades = await get_hospital_units()
    unidades_dicts = [
        {"nome": u["nome"], "ocupacao": u["ocupacao"], "espera_min": u["espera_min"], "status": u["status"]}
        for u in unidades
    ]
    criticos = [u["status"] == "CRITICAL" for u in unidades]
    return {
        "output": {
            "status_geral": "CRITICAL" if any(criticos) else "NORMAL",
            "unidades": unidades_dicts,
            "acoes_imediatas": [
                "Bed contingency plan",
                "Urgent care prioritized",
                "Additional on-call physician activated in ER",
            ],
        }
    }


def build_scoring_graph() -> StateGraph:
    builder = StateGraph(ScoringState)

    builder.add_node("priorizacao_filas", run_priorizacao)
    builder.add_node("predicao_glosa", run_predicao_glosa)
    builder.add_node("predicao_noshow", run_predicao_noshow)
    builder.add_node("conferencia_documental", run_conferencia_documental)
    builder.add_node("agendamento_cirurgico", run_agendamento_cirurgico)
    builder.add_node("gargalos", run_gargalos)
    builder.add_node("monitoramento", run_monitoramento)

    def router(state: ScoringState) -> str:
        return state["workflow"]

    builder.add_conditional_edges(START, router, {
        "priorizacao_filas": "priorizacao_filas",
        "predicao_glosa": "predicao_glosa",
        "predicao_noshow": "predicao_noshow",
        "conferencia_documental": "conferencia_documental",
        "agendamento_cirurgico": "agendamento_cirurgico",
        "gargalos": "gargalos",
        "monitoramento": "monitoramento",
    })

    for node in ["priorizacao_filas", "predicao_glosa", "predicao_noshow",
                  "conferencia_documental", "agendamento_cirurgico",
                  "gargalos", "monitoramento"]:
        builder.add_edge(node, END)

    return builder.compile()
