from src.models.clinical import RiscoClinico
from src.models.operational import (
    SolicitacaoRegulatoria, Prioridade, ItemFilaPriorizada,
    ContaHospitalar, Consulta,
)


def priorizacao_fila(solicitacao: SolicitacaoRegulatoria) -> ItemFilaPriorizada:
    risco_pontos = {"CRITICO": 50, "ALTO": 40, "MEDIO": 20, "BAIXO": 10}
    sla_estourado = solicitacao.dias_espera > solicitacao.sla_dias

    score = (
        risco_pontos.get(solicitacao.risco_clinico.value, 10)
        + (30 if sla_estourado else 0)
        + min(solicitacao.idade * 0.3, 15)
        + (5 if solicitacao.risco_clinico == RiscoClinico.CRITICO else 0)
    )

    if score >= 80:
        prioridade = Prioridade.CRITICA
    elif score >= 50:
        prioridade = Prioridade.ALTA
    elif score >= 25:
        prioridade = Prioridade.MEDIA
    else:
        prioridade = Prioridade.BAIXA

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
        fatores.append("Laudo médico ausente")
    if not conta["tem_relatorio_cirurgico"]:
        score += 20
        fatores.append("Relatório cirúrgico ausente")
    if not conta["tem_evolucoes"]:
        score += 15
        fatores.append("Evoluções diárias ausentes")
    if not conta["tem_opme_autorizada"]:
        score += 15
        fatores.append("OPME sem autorização prévia")
    if not conta["cid_compativel"]:
        score += 15
        fatores.append("CID incompatível com procedimento")

    score += conta["historico_glosa_convenio"] * 100

    if score >= 60:
        classificacao = Prioridade.CRITICA
        acao = "Auditoria imediata"
    elif score >= 40:
        classificacao = Prioridade.ALTA
        acao = "Revisão documental urgente"
    elif score >= 15:
        classificacao = Prioridade.MEDIA
        acao = "Conferir documentação"
    else:
        classificacao = Prioridade.BAIXA
        acao = "Prosseguir com faturamento"

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
        fatores.append("Não confirmou presença")

    score += consulta["taxa_historica_faltas"] * 100

    if consulta["distancia_km"] > 20:
        score += 15
        fatores.append("Grande distância do domicílio")
    elif consulta["distancia_km"] > 10:
        score += 5

    if consulta["plano"] == "Particular":
        score += 10
        fatores.append("Atendimento particular")

    if consulta["tipo"] == "Exame" and not consulta["confirmou"]:
        score += 10
        fatores.append("Exame sem confirmação")

    score = min(score, 100)

    if score >= 60:
        risco = Prioridade.ALTA.value
        acao = "Ligar imediatamente"
    elif score >= 30:
        risco = Prioridade.MEDIA.value
        acao = "Enviar lembrete WhatsApp/SMS"
    else:
        risco = Prioridade.BAIXA.value
        acao = "Manter agenda normalmente"

    return {
        "paciente": consulta["paciente"],
        "tipo": consulta["tipo"],
        "probabilidade_noshow": round(score, 1),
        "fatores_risco": fatores,
        "risco": risco,
        "acao_recomendada": acao,
    }
