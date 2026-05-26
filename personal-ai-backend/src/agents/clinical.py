from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Any
import json
import re
from src.tools.llm_tools import (
    resumo_chain, sumarizacao_chain, insights_chain,
    documentacao_chain, regulatorio_chain, followup_chain,
)
from src.db import (
    get_random_patient, get_patient_evolutions_text,
    get_kpi_text, get_clinical_context,
)


class ClinicalState(TypedDict):
    input: dict
    workflow: str
    output: dict


async def resumo_prontuario(state: ClinicalState) -> dict:
    p = await get_random_patient()
    if not p:
        return {"output": {"resumo": "No patient data available."}}
    exames = "BNP 820 pg/mL, Creatinine 1.8 mg/dL, Potassium 3.4 mEq/L"
    evolucao = await get_patient_evolutions_text(p["id"], 1) or "Partial improvement with parenteral diuresis. Oxygen saturation 96% on room air."
    diagnosticos = "; ".join([p["diagnostico_principal"]] + p["comorbidades"])

    result = await resumo_chain.ainvoke({
        "nome": p["nome"], "idade": p["idade"],
        "diagnosticos": diagnosticos, "alergias": "; ".join(p["alergias"]),
        "exames": exames, "evolucao": evolucao,
    })
    return {"output": {"resumo": result, "paciente": p}}


async def sumarizacao_evolucao(state: ClinicalState) -> dict:
    evolucao = await get_patient_evolutions_text(days=7)
    if not evolucao:
        evolucao = "No evolution data available."
    result = await sumarizacao_chain.ainvoke({"evolucao": evolucao, "dias": 7})
    return {"output": {"resumo": result}}


async def insights_dashboard(state: ClinicalState) -> dict:
    kpis = await get_kpi_text()
    if not kpis:
        kpis = "No KPI data available."
    result = await insights_chain.ainvoke({"kpis": kpis})
    return {"output": {"insights": result}}


async def documentacao_clinica(state: ClinicalState) -> dict:
    contexto = await get_clinical_context()
    if not contexto:
        contexto = "No clinical context available."
    texto = state["input"].get("texto_clinico", "")
    result = await documentacao_chain.ainvoke({"contexto": contexto, "texto_clinico": texto})
    try:
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", result.strip())
        parsed = json.loads(cleaned)
        return {"output": parsed}
    except (json.JSONDecodeError, Exception):
        return {"output": {"texto_evolucao_sugerido": result}}


async def copilot_regulatorio(state: ClinicalState) -> dict:
    descricao = state["input"].get("descricao_caso", "")
    result = await regulatorio_chain.ainvoke({"descricao_caso": descricao})
    try:
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", result.strip())
        parsed = json.loads(cleaned)
        return {"output": parsed}
    except (json.JSONDecodeError, Exception):
        return {"output": {"justificativa_clinica": result}}


async def followup_pos_alta(state: ClinicalState) -> dict:
    data = state["input"]
    result = await followup_chain.ainvoke({
        "nome": data.get("nome", "Patient"),
        "idade": data.get("idade", 60),
        "diagnostico": data.get("diagnostico", ""),
        "risco": data.get("risco", "LOW"),
        "comorbidades": data.get("comorbidades", ""),
        "dias_pos_alta": data.get("dias_pos_alta", 3),
    })
    return {"output": {"followup": result}}


def build_clinical_graph() -> StateGraph:
    builder = StateGraph(ClinicalState)

    builder.add_node("resumo_prontuario", resumo_prontuario)
    builder.add_node("sumarizacao_evolucao", sumarizacao_evolucao)
    builder.add_node("insights_dashboard", insights_dashboard)
    builder.add_node("documentacao_clinica", documentacao_clinica)
    builder.add_node("copilot_regulatorio", copilot_regulatorio)
    builder.add_node("followup_pos_alta", followup_pos_alta)

    def router(state: ClinicalState) -> str:
        return state["workflow"]

    builder.add_conditional_edges(START, router, {
        "resumo_prontuario": "resumo_prontuario",
        "sumarizacao_evolucao": "sumarizacao_evolucao",
        "insights_dashboard": "insights_dashboard",
        "documentacao_clinica": "documentacao_clinica",
        "copilot_regulatorio": "copilot_regulatorio",
        "followup_pos_alta": "followup_pos_alta",
    })
    builder.add_edge("resumo_prontuario", END)
    builder.add_edge("sumarizacao_evolucao", END)
    builder.add_edge("insights_dashboard", END)
    builder.add_edge("documentacao_clinica", END)
    builder.add_edge("copilot_regulatorio", END)
    builder.add_edge("followup_pos_alta", END)

    return builder.compile()
