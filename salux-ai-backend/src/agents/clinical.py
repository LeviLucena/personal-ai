from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Any
import json
import re
from src.tools.llm_tools import (
    resumo_chain, sumarizacao_chain, insights_chain,
    documentacao_chain, regulatorio_chain, followup_chain,
)
from src.tools.mock_data import (
    mock_paciente, mock_evolucao_7_dias, mock_kpis,
    mock_contexto_clinico,
)


class ClinicalState(TypedDict):
    input: dict
    workflow: str
    output: dict


async def resumo_prontuario(state: ClinicalState) -> dict:
    p = mock_paciente()
    exames = "BNP 820 pg/mL, Creatinina 1.8 mg/dL, Potássio 3.4 mEq/L"
    evolucao = "Melhora parcial com diurese parenteral. Saturação 96% em ar ambiente."
    diagnosticos = "; ".join([p.diagnostico_principal] + p.comorbidades)

    result = await resumo_chain.ainvoke({
        "nome": p.nome, "idade": p.idade,
        "diagnosticos": diagnosticos, "alergias": "; ".join(p.alergias),
        "exames": exames, "evolucao": evolucao,
    })
    return {"output": {"resumo": result, "paciente": p.model_dump()}}


async def sumarizacao_evolucao(state: ClinicalState) -> dict:
    evolucao = mock_evolucao_7_dias()
    result = await sumarizacao_chain.ainvoke({"evolucao": evolucao, "dias": 7})
    return {"output": {"resumo": result}}


async def insights_dashboard(state: ClinicalState) -> dict:
    kpis = mock_kpis()
    result = await insights_chain.ainvoke({"kpis": kpis})
    return {"output": {"insights": result}}


async def documentacao_clinica(state: ClinicalState) -> dict:
    contexto = mock_contexto_clinico()
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
        "nome": data.get("nome", "Paciente"),
        "idade": data.get("idade", 60),
        "diagnostico": data.get("diagnostico", ""),
        "risco": data.get("risco", "BAIXO"),
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
