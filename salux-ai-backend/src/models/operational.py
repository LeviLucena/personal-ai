from pydantic import BaseModel, Field
from enum import StrEnum
from src.models.clinical import RiscoClinico


class Prioridade(StrEnum):
    CRITICA = "CRITICA"
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAIXA = "BAIXA"


class StatusFaturamento(StrEnum):
    APROVADO = "APROVADO"
    PENDENTE = "PENDENTE"
    BLOQUEADO = "BLOQUEADO"


class StatusGeral(StrEnum):
    CRITICO = "CRITICO"
    ATENCAO = "ATENCAO"
    NORMAL = "NORMAL"


class SolicitacaoRegulatoria(BaseModel):
    id: str
    paciente: str
    idade: int
    cid: str
    procedimento: str
    dias_espera: int
    risco_clinico: RiscoClinico
    sla_dias: int


class ItemFilaPriorizada(BaseModel):
    solicitacao: SolicitacaoRegulatoria
    score_total: float
    prioridade: Prioridade
    sla_estourado: bool


class ContaHospitalar(BaseModel):
    id: str
    paciente: str
    convenio: str
    procedimento: str
    valor: float
    score_risco_glosa: float
    fatores_risco: list[str] = []
    classificacao: Prioridade
    acao_recomendada: str


class Consulta(BaseModel):
    paciente: str
    data: str
    tipo: str
    probabilidade_noshow: float
    fatores_risco: list[str] = []
    risco: Prioridade
    acao_recomendada: str


class Cirurgia(BaseModel):
    id: str
    procedimento: str
    especialidade: str
    urgencia: bool
    duracao_min: int
    sala_alocada: str = ""


class AgendaCirurgica(BaseModel):
    sala: str
    cirurgias: list[Cirurgia]
    utilizacao_percentual: float
