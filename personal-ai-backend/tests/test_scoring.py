import pytest
from src.tools.scoring_tools import priorizacao_fila, predicao_glosa, predicao_noshow
from src.models.operational import SolicitacaoRegulatoria, Prioridade
from src.models.clinical import RiscoClinico


def test_priorizacao_fila_critica():
    sol = SolicitacaoRegulatoria(
        id="REG-001", paciente="Teste", idade=72,
        cid="J18.9", procedimento="Internação",
        dias_espera=14, risco_clinico=RiscoClinico.ALTO, sla_dias=10,
    )
    result = priorizacao_fila(sol)
    assert result.prioridade in (Prioridade.CRITICA, Prioridade.ALTA)
    assert result.sla_estourado is True
    assert result.score_total >= 80


def test_predicao_glosa_critica():
    conta = {
        "id": "CTH-001", "paciente": "Teste", "convenio": "Amil",
        "procedimento": "Cirurgia", "valor": 10000.0,
        "tem_laudo": False, "tem_relatorio_cirurgico": False,
        "tem_evolucoes": False, "tem_opme_autorizada": False,
        "cid_compativel": False, "historico_glosa_convenio": 0.15,
    }
    result = predicao_glosa(conta)
    assert result["classificacao"] == Prioridade.CRITICA.value
    assert len(result["fatores_risco"]) >= 3


def test_predicao_noshow_alto():
    consulta = {
        "paciente": "Teste", "tipo": "Cardiologia",
        "confirmou": False, "taxa_historica_faltas": 0.45,
        "distancia_km": 25, "plano": "Particular", "idade": 35,
    }
    result = predicao_noshow(consulta)
    assert result["risco"] == Prioridade.ALTA.value
    assert result["probabilidade_noshow"] >= 60


def test_predicao_noshow_baixo():
    consulta = {
        "paciente": "Teste", "tipo": "Retorno",
        "confirmou": True, "taxa_historica_faltas": 0.02,
        "distancia_km": 3, "plano": "Bradesco", "idade": 52,
    }
    result = predicao_noshow(consulta)
    assert result["risco"] == Prioridade.BAIXA.value
    assert result["probabilidade_noshow"] < 30
