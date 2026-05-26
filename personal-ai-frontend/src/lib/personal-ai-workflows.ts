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
    label: "Voice Dashboard",
    buildBody: (text) => ({ comando: text }),
    transformResponse: (data) => data,
  },
  wf07: {
    url: `${BASE}/workflow`,
    tag: "WF-07",
    label: "Clinical Documentation",
    buildBody: (text) => ({ workflow: "documentacao_clinica", input: { texto_clinico: text } }),
    transformResponse: (data) => {
      const output = (data.output || data) as Record<string, unknown>;
      return output;
    },
  },
  wf08: {
    url: `${BASE}/workflow`,
    tag: "WF-08",
    label: "Regulatory Copilot",
    buildBody: (text) => ({ workflow: "copilot_regulatorio", input: { descricao_caso: text } }),
    transformResponse: (data) => {
      const output = (data.output || data) as Record<string, unknown>;
      return output;
    },
  },
  wf12: {
    url: `${BASE}/chat`,
    tag: "WF-12",
    label: "Conversational Copilot",
    buildBody: (text, perfil = "executivo") => ({ message: text, perfil }),
    transformResponse: (data) => ({ resposta: data.resposta }),
  },
};

export function detectDashboardType(text: string): "executivo" | "financeiro" | "regulatorio" | "operacional" | "agenda" {
  const l = text.toLowerCase();
  if (/financ|denial|glosa|revenue|billing|inadimpl/.test(l)) return "financeiro";
  if (/regulat|queue|authori|appeal/.test(l)) return "regulatorio";
  if (/operac|bottleneck|surg|capacit/.test(l)) return "operacional";
  if (/agenda|consult|no.?show|missed|schedule/.test(l)) return "agenda";
  return "executivo";
}

export const dashboardModes: Record<string, ModoChip[]> = {
  executivo:   [{ label: "Summary", value: "resumido" }, { label: "Insights", value: "insights" }, { label: "Units", value: "unidades" }],
  financeiro:  [{ label: "Denials", value: "glosas" }, { label: "Documents", value: "documentos" }],
  regulatorio: [{ label: "Queue", value: "fila" }, { label: "AI Analysis", value: "analise" }],
  operacional: [{ label: "Bottlenecks", value: "gargalos" }, { label: "Monitoring", value: "monitoramento" }, { label: "Surgical", value: "cirurgico" }],
  agenda:      [{ label: "No-show", value: "noshow" }, { label: "Surgical", value: "cirurgico" }],
};

const DASH_KW = ["status", "hospital", "financial", "risk", "regulatory", "bottleneck", "operational", "agenda", "dashboard", "panel", "executive", "forecast", "occupancy", "beds"];
const REG_KW = ["denial", "authorization", "audit", "tiss", "ans", "extension", "regulatory request"];
const DOC_KW = ["document", "evolution", "chart", "record", "anamnesis", "prescription", "report", "admission", "discharge", "cid", "diagnosis"];

export function detectWF(text: string): WorkflowKey {
  const l = text.toLowerCase();
  if (DASH_KW.some((k) => l.includes(k))) return "wf16";
  if (REG_KW.some((k) => l.includes(k))) return "wf08";
  if (DOC_KW.some((k) => l.includes(k))) return "wf07";
  return "wf12";
}

export const exampleQueries: Array<{ text: string; tag: string }> = [
  { text: "Hospital status", tag: "WF-16" },
  { text: "Financial risk", tag: "WF-16" },
  { text: "Regulatory queue", tag: "WF-16" },
  { text: "Operational bottlenecks", tag: "WF-16" },
  { text: "Today's agenda", tag: "WF-16" },
  { text: "What is the current occupancy rate?", tag: "WF-12" },
  { text: "How many patients are waiting in the ICU?", tag: "WF-12" },
  { text: "Is there any critical financial risk today?", tag: "WF-12" },
  { text: "Which surgeries are scheduled for tomorrow?", tag: "WF-12" },
  { text: "Patient John, 65, hypertension, admitted with chest pain", tag: "WF-07" },
  { text: "Evolution: patient stable, blood pressure controlled, no complaints", tag: "WF-07" },
  { text: "Medical discharge after clinical improvement, medication guidance", tag: "WF-07" },
  { text: "Patient with CID I50.0, hospitalized for 5 days, awaiting authorization", tag: "WF-08" },
  { text: "Extension request for elective cardiac surgery", tag: "WF-08" },
  { text: "Denial due to missing medical report, how to appeal?", tag: "WF-08" },
];
