from pydantic import BaseModel
from src.models.operational import StatusGeral, Prioridade


class UnidadeMonitorada(BaseModel):
    nome: str
    ocupacao_percentual: float
    tempo_espera_min: int
    status: StatusGeral


class AlertaOperacional(BaseModel):
    unidade: str
    mensagem: str
    severidade: Prioridade
    acao: str


class PrevisaoGargalo(BaseModel):
    unidade: str
    fila_espera: int
    tempo_medio_espera_min: int
    ocupacao_percentual: float
    status: StatusGeral
    acoes: list[str] = []


class Insight(BaseModel):
    indicador: str
    situacao: str
    acao_sugerida: str


class DashboardExecutivo(BaseModel):
    timestamp: str
    status_operacional: StatusGeral
    alertas_ativos: int
    unidades_criticas: list[str] = []
    top_insights: list[Insight] = []
    analise_ia: str
    resumo_executivo: str
    prioridade_intervencao: list[str] = []
