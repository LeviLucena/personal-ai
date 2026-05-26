export type WorkflowKey = "wf16" | "wf07" | "wf08" | "wf12";

export interface Workflow {
  url: string;
  tag: string;
  label: string;
  buildBody: (text: string, perfil?: string, modo?: string) => Record<string, unknown>;
  transformResponse: (data: Record<string, unknown>) => Record<string, unknown>;
}

export interface ModoChip {
  label: string;
  value: string;
}

const BASE = import.meta.env.VITE_API_BASE_URL as string || "http://localhost:8000";

export const workflows: Record<WorkflowKey, Workflow> = {
  wf16: {
    url: `${BASE}/dashboard`,
    tag: "WF-16",
    label: "Dashboard por voz",
    buildBody: (text) => ({ comando: text }),
    transformResponse: (data) => data,
  },
  wf07: {
    url: `${BASE}/workflow`,
    tag: "WF-07",
    label: "Documentação clínica",
    buildBody: (text) => ({ workflow: "documentacao_clinica", input: { texto_clinico: text } }),
    transformResponse: (data) => {
      const output = (data.output || data) as Record<string, unknown>;
      return output;
    },
  },
  wf08: {
    url: `${BASE}/workflow`,
    tag: "WF-08",
    label: "Copiloto regulatório",
    buildBody: (text) => ({ workflow: "copilot_regulatorio", input: { descricao_caso: text } }),
    transformResponse: (data) => {
      const output = (data.output || data) as Record<string, unknown>;
      return output;
    },
  },
  wf12: {
    url: `${BASE}/chat`,
    tag: "WF-12",
    label: "Copiloto conversacional",
    buildBody: (text, perfil = "executivo") => ({ message: text, perfil }),
    transformResponse: (data) => ({ resposta: data.resposta }),
  },
};

export function detectDashboardType(text: string): "executivo" | "financeiro" | "regulatorio" | "operacional" | "agenda" {
  const l = text.toLowerCase();
  if (/financ|glosa|faturamento|receita|conta|inadimpl/.test(l)) return "financeiro";
  if (/regulat|fila|autoriza|solicit/.test(l)) return "regulatorio";
  if (/operac|gargalo|centro cirurg|capacidade/.test(l)) return "operacional";
  if (/agenda|consulta|no.?show|falta|marcad/.test(l)) return "agenda";
  return "executivo";
}

export const dashboardModes: Record<string, ModoChip[]> = {
  executivo:   [{ label: "Resumido", value: "resumido" }, { label: "Insights", value: "insights" }, { label: "Unidades", value: "unidades" }],
  financeiro:  [{ label: "Glosas", value: "glosas" }, { label: "Documentos", value: "documentos" }],
  regulatorio: [{ label: "Fila", value: "fila" }, { label: "Análise IA", value: "analise" }],
  operacional: [{ label: "Gargalos", value: "gargalos" }, { label: "Monitoramento", value: "monitoramento" }, { label: "Cirúrgico", value: "cirurgico" }],
  agenda:      [{ label: "No-show", value: "noshow" }, { label: "Cirúrgico", value: "cirurgico" }],
};

const DASH_KW = ["status", "hospital", "financeiro", "risco", "regulatória", "regulatoria", "gargalo", "operacional", "agenda", "dashboard", "painel", "executivo", "previsão", "previsao", "ocupação", "ocupacao", "leitos"];
const REG_KW = ["glosa", "autorização", "autorizacao", "auditoria", "tiss", "ans", "prorrogação", "prorrogacao", "solicitação regulatoria"];
const DOC_KW = ["documenta", "evolução", "evolucao", "prontuário", "prontuario", "anamnese", "prescrição", "prescricao", "laudo", "admitido", "alta médica", "cid", "diagnóstico"];

export function detectWF(text: string): WorkflowKey {
  const l = text.toLowerCase();
  if (DASH_KW.some((k) => l.includes(k))) return "wf16";
  if (REG_KW.some((k) => l.includes(k))) return "wf08";
  if (DOC_KW.some((k) => l.includes(k))) return "wf07";
  return "wf12";
}

export const exampleQueries: Array<{ text: string; tag: string }> = [
  { text: "Status do hospital", tag: "WF-16" },
  { text: "Risco financeiro", tag: "WF-16" },
  { text: "Fila regulatória", tag: "WF-16" },
  { text: "Gargalos operacionais", tag: "WF-16" },
  { text: "Agenda de hoje", tag: "WF-16" },
  { text: "Qual a taxa de ocupação atual?", tag: "WF-12" },
  { text: "Quantos pacientes estão em espera na UTI?", tag: "WF-12" },
  { text: "Há algum risco financeiro crítico hoje?", tag: "WF-12" },
  { text: "Quais cirurgias estão agendadas para amanhã?", tag: "WF-12" },
  { text: "Paciente João, 65 anos, hipertensão, admitido com dor torácica", tag: "WF-07" },
  { text: "Evolução: paciente estável, pressão controlada, sem queixas", tag: "WF-07" },
  { text: "Alta médica após melhora clínica, orientado sobre medicação", tag: "WF-07" },
  { text: "Paciente com CID I50.0, internado há 5 dias, aguardando autorização", tag: "WF-08" },
  { text: "Pedido de prorrogação para cirurgia cardíaca eletiva", tag: "WF-08" },
  { text: "Glosa por falta de relatório médico, como recorrer?", tag: "WF-08" },
];
