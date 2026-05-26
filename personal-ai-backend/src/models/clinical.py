from pydantic import BaseModel, Field
from enum import StrEnum
from datetime import date, datetime


class RiscoClinico(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TendenciaClinica(StrEnum):
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    WORSENING = "WORSENING"


class Paciente(BaseModel):
    id: str
    nome: str
    idade: int
    diagnostico_principal: str
    comorbidades: list[str] = []
    alergias: list[str] = []
    data_internacao: date
    leito: str = ""
    especialidade: str = ""


class ResumoProntuario(BaseModel):
    paciente: Paciente
    resumo: str
    alertas_criticos: list[str] = []


class SumarizacaoEvolucao(BaseModel):
    paciente_id: str
    periodo_dias: int
    resumo_periodo: str
    principais_intercorrencias: list[str] = []
    tendencia_clinica: TendenciaClinica
    condutas_realizadas: list[str] = []
    proximos_passos: list[str] = []
    risco_atual: RiscoClinico


class TextoEvolucaoSugerido(BaseModel):
    texto: str
    qualidade_estimada: str
    campos_preenchidos: list[str] = []
    campos_faltantes: list[str] = []
    alertas: list[str] = []
