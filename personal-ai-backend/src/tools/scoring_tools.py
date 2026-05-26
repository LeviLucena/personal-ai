from src.models.clinical import RiscoClinico
from src.models.operational import (
    SolicitacaoRegulatoria, Prioridade, ItemFilaPriorizada,
    ContaHospitalar, Consulta,
)


def priorizacao_fila(solicitacao: SolicitacaoRegulatoria) -> ItemFilaPriorizada:
    risco_pontos = {"CRITICAL": 50, "HIGH": 40, "MEDIUM": 20, "LOW": 10}
    sla_estourado = solicitacao.dias_espera > solicitacao.sla_dias

    score = (
        risco_pontos.get(solicitacao.risco_clinico.value, 10)
        + (30 if sla_estourado else 0)
        + min(solicitacao.idade * 0.3, 15)
        + (5 if solicitacao.risco_clinico == RiscoClinico.CRITICAL else 0)
    )

    if score >= 80:
        prioridade = Prioridade.CRITICAL
    elif score >= 50:
        prioridade = Prioridade.HIGH
    elif score >= 25:
        prioridade = Prioridade.MEDIUM
    else:
        prioridade = Prioridade.LOW

    return ItemFilaPriorizada(
        solicitacao=solicitacao,
        score_total=round(score, 1),
        prioridade=prioridade,
        sla_estourado=sla_estourado,
    )


def predicao_glosa(conta: dict) -> dict:
    score = 0
    fatores = []

    if not conta["tem_laudo"]:
        score += 25
        fatores.append("Medical report missing")
    if not conta["tem_relatorio_cirurgico"]:
        score += 20
        fatores.append("Surgical report missing")
    if not conta["tem_evolucoes"]:
        score += 15
        fatores.append("Daily progress notes missing")
    if not conta["tem_opme_autorizada"]:
        score += 15
        fatores.append("OPME without prior authorization")
    if not conta["cid_compativel"]:
        score += 15
        fatores.append("ICD incompatible with procedure")

    score += conta["historico_glosa_convenio"] * 100

    if score >= 60:
        classificacao = Prioridade.CRITICAL
        acao = "Immediate audit"
    elif score >= 40:
        classificacao = Prioridade.HIGH
        acao = "Urgent document review"
    elif score >= 15:
        classificacao = Prioridade.MEDIUM
        acao = "Check documentation"
    else:
        classificacao = Prioridade.LOW
        acao = "Proceed with billing"

    return {
        "id": conta["id"],
        "paciente": conta["paciente"],
        "convenio": conta["convenio"],
        "procedimento": conta["procedimento"],
        "valor": conta["valor"],
        "score_risco_glosa": round(min(score, 100), 1),
        "fatores_risco": fatores,
        "classificacao": classificacao.value,
        "valor_em_risco": round(conta["valor"] * min(score, 100) / 100, 2),
        "acao_recomendada": acao,
    }


def predicao_noshow(consulta: dict) -> dict:
    score = 0
    fatores = []

    if not consulta["confirmou"]:
        score += 30
        fatores.append("Did not confirm attendance")

    score += consulta["taxa_historica_faltas"] * 100

    if consulta["distancia_km"] > 20:
        score += 15
        fatores.append("Long distance from residence")
    elif consulta["distancia_km"] > 10:
        score += 5

    if consulta["plano"] == "Particular":
        score += 10
        fatores.append("Private care")

    if consulta["tipo"] == "Exame" and not consulta["confirmou"]:
        score += 10
        fatores.append("Exam without confirmation")

    score = min(score, 100)

    if score >= 60:
        risco = Prioridade.HIGH.value
        acao = "Call immediately"
    elif score >= 30:
        risco = Prioridade.MEDIUM.value
        acao = "Send WhatsApp/SMS reminder"
    else:
        risco = Prioridade.LOW.value
        acao = "Maintain schedule normally"

    return {
        "paciente": consulta["paciente"],
        "tipo": consulta["tipo"],
        "probabilidade_noshow": round(score, 1),
        "fatores_risco": fatores,
        "risco": risco,
        "acao_recomendada": acao,
    }
