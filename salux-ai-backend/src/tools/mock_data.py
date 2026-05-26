from src.models.clinical import (
    Paciente, ResumoProntuario, SumarizacaoEvolucao,
    TextoEvolucaoSugerido, RiscoClinico, TendenciaClinica,
)
from src.models.operational import (
    SolicitacaoRegulatoria, ItemFilaPriorizada, Prioridade,
    ContaHospitalar, Consulta, Cirurgia, AgendaCirurgica, StatusGeral,
)
from src.models.financial import (
    UnidadeMonitorada, AlertaOperacional, PrevisaoGargalo,
    Insight, DashboardExecutivo,
)
from datetime import date


def mock_paciente() -> Paciente:
    return Paciente(
        id="PAC-2024-001",
        nome="João Silva",
        idade=65,
        diagnostico_principal="ICC (I50.0)",
        comorbidades=["Hipertensão (I10)", "Diabetes tipo 2 (E11)"],
        alergias=["Dipirona", "Penicilina"],
        data_internacao=date(2024, 4, 8),
        leito="204-A",
        especialidade="Cardiologia",
    )


def mock_evolucao_7_dias() -> str:
    return """04/04 - Paciente admitida com sepse de foco pulmonar. Glasgow 15, PA 90x60, FC 110, SatO2 91% em ar ambiente. Iniciado antibioticoterapia com Ceftriaxona + Azitromicina.
05/04 - Mantém febre (38.5°C), PA 100x65 com noradrenalina 0.3mcg/kg/min. Culturas coletadas. PCR 180.
06/04 - Redução gradual de noradrenalina. Antibiograma mostra sensibilidade à Ceftriaxona. Mantido plano.
07/04 - Pico febril 38.8°C pela manhã. Suspeita de foco secundário. Iniciado investigação.
08/04 - Afebril há 24h. Desmame de noradrenalina concluído. Iniciado desmame VNI.
09/04 - Mantém SatO2 96% em ar ambiente. Transferência para enfermaria programada.
10/04 - Transferida para enfermaria clínica. PA 120x75, FC 82, SatO2 97%. Alta planejada para 12/04."""


def mock_kpis() -> str:
    return """=== INDICADORES ASSISTENCIAIS ===
Taxa de ocupação: 87.5% (meta < 85%)
Tempo médio de espera PS: 42min (meta < 30min)
Taxa de reinternação em 7 dias: 4.2% (meta < 5%)

=== INDICADORES OPERACIONAIS ===
Taxa de no-show ambulatorial: 18.5% (meta < 12%)
Centro cirúrgico: 74% ocupação
Produtividade de leitos: 3.2 dias permanência média (meta < 4)

=== INDICADORES FINANCEIROS ===
Receita total: R$ 4.850.000 (meta R$ 5.200.000)
Margem operacional: 11.2% (meta > 15%)
Taxa de glosas: 6.8% (meta < 4%)
Inadimplência: 3.5% (meta < 5%)"""


def mock_fila_regulatoria() -> list[SolicitacaoRegulatoria]:
    return [
        SolicitacaoRegulatoria(id="REG-001", paciente="Luíza Fernandes", idade=72, cid="J18.9", procedimento="Internação Pneumonia", dias_espera=14, risco_clinico=RiscoClinico.ALTO, sla_dias=10),
        SolicitacaoRegulatoria(id="REG-002", paciente="José Santos", idade=80, cid="I50.0", procedimento="Internação ICC", dias_espera=12, risco_clinico=RiscoClinico.ALTO, sla_dias=10),
        SolicitacaoRegulatoria(id="REG-003", paciente="Carlos Andrade", idade=68, cid="I21.0", procedimento="Cateterismo Cardíaco", dias_espera=20, risco_clinico=RiscoClinico.ALTO, sla_dias=15),
        SolicitacaoRegulatoria(id="REG-004", paciente="Ana Beatriz", idade=45, cid="C50.9", procedimento="Quimioterapia", dias_espera=8, risco_clinico=RiscoClinico.CRITICO, sla_dias=7),
        SolicitacaoRegulatoria(id="REG-005", paciente="Roberto Maia", idade=60, cid="E11", procedimento="Internação DM2", dias_espera=5, risco_clinico=RiscoClinico.MEDIO, sla_dias=7),
    ]


def mock_contas_hospitalares() -> list[dict]:
    return [
        {"id": "CTH-1003", "paciente": "Paciente A", "convenio": "SulAmérica", "procedimento": "Artroscopia joelho", "valor": 12500.0, "tem_laudo": False, "tem_relatorio_cirurgico": False, "tem_evolucoes": True, "tem_opme_autorizada": False, "cid_compativel": True, "historico_glosa_convenio": 0.15},
        {"id": "CTH-1005", "paciente": "Paciente B", "convenio": "Amil", "procedimento": "Endoscopia", "valor": 3500.0, "tem_laudo": True, "tem_relatorio_cirurgico": False, "tem_evolucoes": False, "tem_opme_autorizada": True, "cid_compativel": True, "historico_glosa_convenio": 0.08},
        {"id": "CTH-1002", "paciente": "Paciente C", "convenio": "Unimed", "procedimento": "Cateterismo", "valor": 8500.0, "tem_laudo": True, "tem_relatorio_cirurgico": True, "tem_evolucoes": True, "tem_opme_autorizada": True, "cid_compativel": True, "historico_glosa_convenio": 0.03},
        {"id": "CTH-1001", "paciente": "Paciente D", "convenio": "Amil", "procedimento": "Colecistectomia", "valor": 7200.0, "tem_laudo": True, "tem_relatorio_cirurgico": True, "tem_evolucoes": True, "tem_opme_autorizada": False, "cid_compativel": True, "historico_glosa_convenio": 0.08},
        {"id": "CTH-1004", "paciente": "Paciente E", "convenio": "Bradesco", "procedimento": "Parto cesáreo", "valor": 9600.0, "tem_laudo": True, "tem_relatorio_cirurgico": True, "tem_evolucoes": True, "tem_opme_autorizada": True, "cid_compativel": True, "historico_glosa_convenio": 0.02},
    ]


def mock_agenda_consultas() -> list[dict]:
    return [
        {"paciente": "Diego Carvalho", "tipo": "Cardiologia", "confirmou": False, "taxa_historica_faltas": 0.45, "distancia_km": 25, "plano": "Particular", "idade": 35},
        {"paciente": "Rogério Lima", "tipo": "Retorno", "confirmou": True, "taxa_historica_faltas": 0.30, "distancia_km": 15, "plano": "Unimed", "idade": 28},
        {"paciente": "Marcos Vieira", "tipo": "Exame", "confirmou": False, "taxa_historica_faltas": 0.20, "distancia_km": 8, "plano": "Amil", "idade": 45},
        {"paciente": "Sonia Prado", "tipo": "Retorno", "confirmou": True, "taxa_historica_faltas": 0.02, "distancia_km": 3, "plano": "Bradesco", "idade": 52},
        {"paciente": "Clara Nunes", "tipo": "Pediatria", "confirmou": True, "taxa_historica_faltas": 0.00, "distancia_km": 5, "plano": "SulAmérica", "idade": 8},
        {"paciente": "Pedro Alves", "tipo": "Cardiologia", "confirmou": False, "taxa_historica_faltas": 0.35, "distancia_km": 20, "plano": "Unimed", "idade": 55},
    ]


def mock_contexto_clinico() -> str:
    return """Paciente Roberto Ferreira, 58 anos, internado com ICC descompensada (CID I50.0) desde 08/04/2026.
Sinais vitais: PA 136/88 mmHg, FC 78 bpm, SatO2 96%, temperatura 36.5°C, peso 78kg.
Medicações: Furosemida 40mg 12/12h, Enalapril 10mg/dia, Carvedilol 12.5mg/dia.
Exames: BNP 480 pg/mL, Creatinina 1.4 mg/dL, Potássio 4.2 mEq/L.
Evolução: melhora do quadro respiratório, sem febre nas últimas 12h, mantendo antibioticoterapia."""


def mock_unidades() -> list[dict]:
    return [
        {"nome": "Pronto Socorro", "ocupacao": 98, "espera_min": 85, "status": StatusGeral.CRITICO},
        {"nome": "UTI Geral", "ocupacao": 95, "espera_min": 120, "status": StatusGeral.CRITICO},
        {"nome": "Enfermaria Clínica", "ocupacao": 82, "espera_min": 45, "status": StatusGeral.NORMAL},
        {"nome": "Centro Cirúrgico", "ocupacao": 74, "espera_min": 20, "status": StatusGeral.NORMAL},
        {"nome": "Ambulatório", "ocupacao": 65, "espera_min": 35, "status": StatusGeral.NORMAL},
    ]
