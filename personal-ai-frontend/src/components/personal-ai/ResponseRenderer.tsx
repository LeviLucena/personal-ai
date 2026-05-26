/* eslint-disable @typescript-eslint/no-explicit-any */
import { AlertTriangle, CheckCircle2, Sparkles } from "lucide-react";

/**
 * Renders Personal AI workflow responses in a readable format.
 * Supports: WF-16 (dashboards), WF-07 (documentation), WF-08 (regulatory), WF-12 (conversational)
 * Falls back intelligently to raw JSON if structure is unrecognized.
 */
export function ResponseRenderer({ data, tag }: { data: any; tag: string }) {
  if (!data) return null;

  // WF-12 — copiloto conversacional (resposta livre)
  if (tag === "WF-12") return <ConversationalView data={data} />;

  // WF-16 — dashboards
  if (tag === "WF-16" || data.dashboard) return <DashboardView data={data} />;

  // WF-07 — clinical documentation
  if (tag === "WF-07" || data.evolucao_estruturada || data.documentacao) {
    return <ClinicalView data={data} />;
  }

  // WF-08 — regulatory
  if (tag === "WF-08" || data.analise_regulatoria || data.recomendacao) {
    return <RegulatoryView data={data} />;
  }

  return <RawJson data={data} />;
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-[11px] font-semibold uppercase tracking-[0.12em] text-white/55 mb-2">
      {children}
    </h3>
  );
}

function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`rounded-2xl bg-white/5 border border-white/10 p-4 ${className}`}>
      {children}
    </div>
  );
}

/* ---------- Conversational (WF-12) ---------- */
function ConversationalView({ data }: { data: any }) {
  const main = data.resposta || data.answer || data.message || data.texto || (typeof data === "string" ? data : "");
  const sugestao = data.sugestao || data.suggestion;
  const alerta = data.alerta || data.alert;

  return (
    <div className="space-y-4">
      {main && (
        <p className="text-[15px] leading-relaxed text-white/90 whitespace-pre-wrap">{main}</p>
      )}
      {alerta && (
        <div className="rounded-xl bg-amber-500/10 border border-amber-400/30 p-3.5 flex gap-3">
          <AlertTriangle className="w-4 h-4 text-amber-300 shrink-0 mt-0.5" />
          <div className="text-sm text-amber-100">
            {typeof alerta === "string" ? alerta : <pre className="whitespace-pre-wrap font-sans">{JSON.stringify(alerta, null, 2)}</pre>}
          </div>
        </div>
      )}
      {sugestao && (
        <button className="w-full text-left rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 p-3.5 transition-colors">
          <div className="text-[11px] uppercase tracking-wider text-white/45 mb-1">Suggestion</div>
          <div className="text-sm text-white/85">{typeof sugestao === "string" ? sugestao : JSON.stringify(sugestao)}</div>
        </button>
      )}
      {!main && !sugestao && !alerta && <RawJson data={data} />}
    </div>
  );
}

/* ---------- Dashboard (WF-16) ---------- */
function DashboardView({ data }: { data: any }) {
  const tipo = String(data.dashboard || "").toUpperCase();
  const titles: Record<string, string> = {
    EXECUTIVO: "Executive Dashboard",
    FINANCEIRO: "Financial Dashboard",
    REGULATORIO: "Regulatory Dashboard",
    OPERACIONAL: "Operational Dashboard",
    AGENDA: "Schedule Dashboard",
  };

  return (
    <div className="space-y-4">
      {/* Header with AI analysis */}
      {(data.analise_ia || data.resumo_executivo) && (
        <div>
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-300" />
            {titles[tipo] || tipo || "Dashboard"}
          </h2>
          {data.resumo_executivo && (
            <p className="mt-2 text-sm text-white/80 leading-relaxed">{data.resumo_executivo}</p>
          )}
          {data.analise_ia && !data.resumo_executivo && (
            <p className="mt-2 text-sm text-white/75 leading-relaxed">{data.analise_ia}</p>
          )}
        </div>
      )}

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {data.status_operacional && (
          <Kpi
            label="Operational status"
            value={data.status_operacional === "CRITICAL" ? "🔴 Critical" : data.status_operacional}
            tone={data.status_operacional === "CRITICAL" ? "danger" : "ok"}
          />
        )}
        {data.alertas_ativos !== undefined && (
          <Kpi label="Active alerts" value={data.alertas_ativos} sub={data.fonte} tone={data.alertas_ativos > 3 ? "danger" : data.alertas_ativos > 0 ? "warn" : "ok"} />
        )}
        {data.glosas?.criticas !== undefined && (
          <Kpi label="Critical glosas" value={data.glosas.criticas} sub={`${data.glosas.total_contas ?? 0} accounts`} tone="danger" />
        )}
        {data.glosas?.valor_total_em_risco && (
          <Kpi label="Value at risk" value={data.glosas.valor_total_em_risco} sub="glosas" tone="warn" />
        )}
        {data.fila?.sla_estourado !== undefined && (
          <Kpi label="SLA breached" value={data.fila.sla_estourado} sub={`${data.fila.total ?? 0} in queue`} tone={data.fila.sla_estourado > 0 ? "danger" : "ok"} />
        )}
        {data.documentacao?.score_completude !== undefined && (
          <Kpi label="Completeness" value={`${data.documentacao.score_completude}%`} sub={data.documentacao.status_faturamento} tone={data.documentacao.score_completude >= 80 ? "ok" : data.documentacao.score_completude >= 60 ? "warn" : "danger"} />
        )}
        {data.no_show?.alto_risco !== undefined && (
          <Kpi label="High no-show risk" value={data.no_show.alto_risco} sub={`${data.no_show.total_consultas ?? 0} appointments`} tone="warn" />
        )}
      </div>

      {/* Resumo financeiro */}
      {data.documentacao?.documentos_faltantes?.length > 0 && (
        <div>
          <SectionTitle>Missing documents</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {data.documentacao.documentos_faltantes.map((doc: string, i: number) => (
              <span key={i} className="px-2.5 py-1 rounded-md bg-amber-500/15 border border-amber-400/30 text-xs text-amber-200">
                {doc}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Top insights / unidades / contas */}
      {Array.isArray(data.top_insights) && data.top_insights.length > 0 && (
        <div>
          <SectionTitle>Priority insights</SectionTitle>
          <div className="space-y-2">
            {data.top_insights.slice(0, 6).map((i: any, idx: number) => (
              <ListRow key={idx} title={i.indicador || i.titulo || "—"} status={i.situacao || i.acao} desc={i.acao || i.descricao} />
            ))}
          </div>
        </div>
      )}

      {Array.isArray(data.unidades_criticas) && data.unidades_criticas.length > 0 && (
        <div>
          <SectionTitle>Critical units</SectionTitle>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {data.unidades_criticas.map((u: any, i: number) => (
              <div key={i} className="rounded-xl bg-red-500/10 border border-red-400/30 p-2.5 text-center">
                <div className="text-xs text-white/85 font-medium truncate">{u}</div>
                {typeof u === "object" && u.ocupacao !== undefined && <div className="text-lg font-bold text-red-300">{u.ocupacao}%</div>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Glosas - risco */}
      {Array.isArray(data.glosas?.top_risco) && data.glosas.top_risco.length > 0 && (
        <div>
          <SectionTitle>Accounts with highest glosa risk</SectionTitle>
          <div className="space-y-1.5">
            {data.glosas.top_risco.slice(0, 6).map((c: any, i: number) => (
              <ScoreRow key={i} label={c.conta || `Account ${i + 1}`} score={c.score} badge={c.acao} />
            ))}
          </div>
        </div>
      )}

      {/* Regulatory queue */}
      {Array.isArray(data.fila?.top_prioritarios) && data.fila.top_prioritarios.length > 0 && (
        <div>
          <SectionTitle>Priority patients</SectionTitle>
          <div className="space-y-1.5">
            {data.fila.top_prioritarios.map((p: any, i: number) => (
              <ScoreRow key={i} label={p.paciente} score={p.score} badge={p.prioridade || p.sla} extra={p.cid} />
            ))}
          </div>
        </div>
      )}

      {/* Gargalos operacionais */}
      {data.gargalos && (
        <div>
          <SectionTitle>Bottleneck predictions</SectionTitle>
          <div className="grid grid-cols-3 gap-3 mb-3">
            {data.gargalos.previsoes && (
              <>
                <Card>
                  <div className="text-[10px] uppercase tracking-wider text-white/50">Patients in queue</div>
                  <div className="text-2xl font-bold text-white">{data.gargalos.previsoes.pacientes_espera}</div>
                </Card>
                <Card>
                  <div className="text-[10px] uppercase tracking-wider text-white/50">Average wait time</div>
                  <div className="text-2xl font-bold text-white">{data.gargalos.previsoes.tempo_medio_espera_min}min</div>
                </Card>
                <Card>
                  <div className="text-[10px] uppercase tracking-wider text-white/50">Occupancy</div>
                  <div className="text-2xl font-bold text-white">{data.gargalos.previsoes.ocupacao_leitos_pct}%</div>
                </Card>
              </>
            )}
          </div>
          {Array.isArray(data.gargalos.top_alertas) && data.gargalos.top_alertas.length > 0 && (
            <>
               <SectionTitle>Priority insights</SectionTitle>
               <div className="space-y-2">
                 {data.gargalos.top_alertas.map((a: any, i: number) => (
                  <AlertRow key={i} message={a.mensagem} severity={a.severidade} />
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Monitoramento de unidades */}
      {Array.isArray(data.monitoramento?.unidades) && data.monitoramento.unidades.length > 0 && (
        <div>
          <SectionTitle>Unit status</SectionTitle>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {data.monitoramento.unidades.map((u: any, i: number) => {
              const statusColor = u.status === "CRITICAL" ? "border-red-400/30 bg-red-500/10"
                : u.status === "WARNING" ? "border-amber-400/30 bg-amber-500/10"
                : "border-white/10 bg-white/5";
              return (
                <div key={i} className={`rounded-xl border p-2.5 ${statusColor}`}>
                  <div className="text-xs text-white/85 font-medium truncate">{u.nome}</div>
                  <div className="text-lg font-bold text-white">{u.ocupacao}%</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* No-show / Agenda */}
      {Array.isArray(data.no_show?.acoes_urgentes) && data.no_show.acoes_urgentes.length > 0 && (
        <div>
          <SectionTitle>Urgent actions - no-show</SectionTitle>
          <div className="space-y-2">
            {data.no_show.acoes_urgentes.map((a: any, i: number) => (
              <ListRow key={i} title={a.paciente} status={a.probabilidade} desc={a.acao} />
            ))}
          </div>
        </div>
      )}

      {/* Surgical center */}
      {data.centro_cirurgico && (
        <div>
          <SectionTitle>Surgical center</SectionTitle>
          <div className="grid grid-cols-2 gap-3">
            <Card>
              <div className="text-[10px] uppercase tracking-wider text-white/50">Allocated surgeries</div>
              <div className="text-2xl font-bold text-white">{data.centro_cirurgico.cirurgias_alocadas}</div>
            </Card>
            <Card>
              <div className="text-[10px] uppercase tracking-wider text-white/50">Not allocated</div>
              <div className="text-2xl font-bold text-amber-300">{data.centro_cirurgico.nao_alocadas}</div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}

function Kpi({ label, value, sub, tone = "default" }: { label: string; value: React.ReactNode; sub?: string; tone?: "ok" | "warn" | "danger" | "default" }) {
  const color =
    tone === "danger" ? "text-red-300" : tone === "warn" ? "text-amber-300" : tone === "ok" ? "text-emerald-300" : "text-white";
  return (
    <Card className="text-center !p-3.5">
      <div className="text-[10px] uppercase tracking-wider text-white/50 mb-1.5">{label}</div>
      <div className={`text-3xl font-bold leading-none ${color}`}>{value}</div>
      {sub && <div className="text-[11px] text-white/45 mt-1.5">{sub}</div>}
    </Card>
  );
}

function ListRow({ title, status, desc }: { title: string; status?: string; desc?: string }) {
  const s = String(status || "").toUpperCase();
  const dot = /CRITICAL/.test(s) ? "bg-red-400" : s.includes("ALERT") ? "bg-amber-400" : "bg-emerald-400";
  return (
    <div className="flex gap-3 rounded-xl bg-white/5 border border-white/10 p-3">
      <div className={`w-1.5 h-1.5 rounded-full mt-2 shrink-0 ${dot}`} />
      <div className="min-w-0">
        <div className="text-sm text-white/90 font-medium">{title}</div>
        {desc && <div className="text-xs text-white/60 mt-1 leading-relaxed">{desc}</div>}
      </div>
    </div>
  );
}

function ScoreRow({ label, score, badge, extra }: { label: string; score?: number; badge?: string; extra?: string }) {
  const v = typeof score === "number" ? score : 0;
  const color = v >= 80 ? "bg-red-400" : v >= 60 ? "bg-amber-400" : "bg-emerald-400";
  return (
    <div className="flex items-center gap-3 rounded-xl bg-white/5 border border-white/10 px-3 py-2.5">
      <div className="flex-1 min-w-0">
        <div className="text-sm text-white/85">{label}</div>
        {extra && <div className="text-[10px] text-white/50 mt-0.5">{extra}</div>}
        {v > 0 && (
          <div className="mt-1.5 h-1.5 rounded-full bg-white/10 overflow-hidden">
            <div className={`h-full ${color}`} style={{ width: `${Math.min(Math.max(v, 0), 100)}%` }} />
          </div>
        )}
      </div>
      {v > 0 && <div className="text-sm font-semibold text-white/90 shrink-0 tabular-nums">{v}</div>}
      {badge && <div className="text-[10px] uppercase tracking-wider text-white/60 shrink-0">{badge}</div>}
    </div>
  );
}

function AlertRow({ message, severity }: { message: string; severity: string }) {
  const colors = severity === "CRITICAL" || severity === "HIGH"
    ? "border-red-400/30 bg-red-500/10 text-red-200"
    : "border-amber-400/30 bg-amber-500/10 text-amber-200";
  return (
    <div className={`flex gap-3 rounded-xl border p-3 ${colors}`}>
      <div className={`w-1.5 h-1.5 rounded-full mt-1.5 shrink-0 ${severity === "CRITICAL" ? "bg-red-400" : "bg-amber-400"}`} />
      <div className="text-sm leading-relaxed">{message}</div>
    </div>
  );
}

/* ---------- Clinical (WF-07) ---------- */
function ClinicalView({ data }: { data: any }) {
  const ev = data.evolucao_estruturada || data.evolucao || {};

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="px-2.5 py-1 rounded-md bg-blue-500/20 text-blue-200 text-[10px] font-bold tracking-wider">WF-07</span>
        <h2 className="text-lg font-semibold text-white">Clinical documentation</h2>
        {data.qualidade_estimada && <QualityBadge q={data.qualidade_estimada} />}
      </div>

      {/* Suggested evolution text (main) */}
      {data.texto_evolucao_sugerido && (
        <Card className="!bg-white/[0.07]">
          <p className="text-sm leading-relaxed text-white/90 whitespace-pre-wrap">{data.texto_evolucao_sugerido}</p>
        </Card>
      )}

      {/* SOAP fields */}
      {(ev.subjetivo || ev.objetivo || ev.avaliacao || ev.plano) && (
        <>
          {ev.subjetivo && <Block title="Subjective" text={ev.subjetivo} />}
          {ev.objetivo && <Block title="Objective" text={ev.objetivo} />}
          {ev.avaliacao && <Block title="Assessment" text={ev.avaliacao} />}
          {ev.plano && <Block title="Plan" text={ev.plano} />}
        </>
      )}

      {/* Campos preenchidos/faltantes */}
      {data.campos_preenchidos?.length > 0 && (
        <div>
          <SectionTitle>Filled fields</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {data.campos_preenchidos.map((c: string, i: number) => (
              <span key={i} className="px-2.5 py-1 rounded-md bg-emerald-500/15 border border-emerald-400/30 text-xs text-emerald-200">
                {c}
              </span>
            ))}
          </div>
        </div>
      )}

      {data.campos_faltantes?.length > 0 && (
        <div>
          <SectionTitle>Fields to complete</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {data.campos_faltantes.map((c: string, i: number) => (
              <span key={i} className="px-2.5 py-1 rounded-md bg-amber-500/15 border border-amber-400/30 text-xs text-amber-200">
                {c}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* CIDs sugeridos */}
      {Array.isArray(data.cids_sugeridos) && data.cids_sugeridos.length > 0 && (
        <div>
          <SectionTitle>Suggested CIDs</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {data.cids_sugeridos.map((c: any, i: number) => (
              <span key={i} className="px-2.5 py-1 rounded-md bg-white/8 border border-white/15 text-xs text-white/85">
                {typeof c === "string" ? c : `${c.codigo || ""} ${c.descricao || ""}`}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Alertas */}
      {(data.alertas_documentacao?.length > 0 || data.alertas?.length > 0) && (
        <div className="space-y-2">
          {(data.alertas_documentacao || data.alertas).map((a: any, i: number) => (
            <div key={i} className="rounded-xl bg-amber-500/10 border border-amber-400/30 p-3 flex gap-3">
              <AlertTriangle className="w-4 h-4 text-amber-300 shrink-0 mt-0.5" />
              <div className="text-sm text-amber-100">{typeof a === "string" ? a : a.mensagem || JSON.stringify(a)}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Block({ title, text }: { title: string; text: string }) {
  return (
    <div>
      <SectionTitle>{title}</SectionTitle>
      <Card>
        <p className="text-sm leading-relaxed text-white/85 whitespace-pre-wrap">{text}</p>
      </Card>
    </div>
  );
}

function QualityBadge({ q }: { q: string }) {
  const v = String(q).toLowerCase();
  const cfg = v.includes("complet") ? { c: "bg-emerald-500/20 text-emerald-200 border-emerald-400/30", icon: <CheckCircle2 className="w-3 h-3" /> }
    : v.includes("parcial") ? { c: "bg-amber-500/20 text-amber-200 border-amber-400/30", icon: <AlertTriangle className="w-3 h-3" /> }
    : { c: "bg-red-500/20 text-red-200 border-red-400/30", icon: <AlertTriangle className="w-3 h-3" /> };
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs font-medium ${cfg.c}`}>
      {cfg.icon}{q}
    </span>
  );
}

/* ---------- Regulatory (WF-08) ---------- */
function RegulatoryView({ data }: { data: any }) {
  const prob = data.probabilidade_aprovacao || data.probabilidade;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="px-2.5 py-1 rounded-md bg-blue-500/20 text-blue-200 text-[10px] font-bold tracking-wider">WF-08</span>
        <h2 className="text-lg font-semibold text-white">Regulatory analysis</h2>
        {prob && <ProbBadge p={prob} />}
      </div>

      {/* Main clinical justification */}
      {data.justificativa_clinica && (
        <Card className="!bg-white/[0.07]">
          <SectionTitle>Clinical justification</SectionTitle>
          <p className="text-sm leading-relaxed text-white/90 whitespace-pre-wrap">{data.justificativa_clinica}</p>
        </Card>
      )}

      {/* Argumentos principais */}
      {data.argumentos_principais?.length > 0 && (
        <div>
          <SectionTitle>Main arguments</SectionTitle>
          <div className="space-y-2">
            {data.argumentos_principais.map((a: string, i: number) => (
              <div key={i} className="flex gap-3 rounded-xl bg-white/5 border border-white/10 p-3">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-2 shrink-0" />
                <p className="text-sm text-white/85">{a}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Scientific evidence */}
      {data.embasamento_cientifico?.length > 0 && (
        <div>
          <SectionTitle>Scientific basis</SectionTitle>
          <div className="space-y-2">
            {data.embasamento_cientifico.map((ref: string, i: number) => (
              <div key={i} className="flex gap-3 rounded-xl bg-white/5 border border-white/10 p-3">
                <div className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-2 shrink-0" />
                <p className="text-sm text-white/80 italic">{ref}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendation / regulatory analysis */}
      {(data.analise_regulatoria || data.recomendacao || data.justificativa) && (
        <>
          {data.analise_regulatoria && <Block title="Analysis" text={data.analise_regulatoria} />}
          {data.recomendacao && <Block title="Recommendation" text={data.recomendacao} />}
          {data.justificativa && !data.justificativa_clinica && <Block title="Justification" text={data.justificativa} />}
        </>
      )}

      {/* Required documents */}
      {data.documentos_necessarios?.length > 0 && (
        <div>
          <SectionTitle>Required documents</SectionTitle>
          <div className="space-y-1.5">
            {data.documentos_necessarios.map((d: string, i: number) => (
              <div key={i} className="flex items-center gap-2.5 rounded-xl bg-white/5 border border-white/10 px-3 py-2.5">
                <div className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                <span className="text-sm text-white/85">{d}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Points of attention */}
      {data.pontos_atencao?.length > 0 && (
        <div>
          <SectionTitle>Points of attention</SectionTitle>
          <div className="space-y-2">
            {data.pontos_atencao.map((p: string, i: number) => (
              <div key={i} className="rounded-xl bg-amber-500/10 border border-amber-400/30 p-3 flex gap-3">
                <AlertTriangle className="w-4 h-4 text-amber-300 shrink-0 mt-0.5" />
                <p className="text-sm text-amber-100">{p}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Documentos pendentes (legacy) */}
      {data.documentos_pendentes?.length > 0 && !data.documentos_necessarios && (
        <div>
          <SectionTitle>Pending documents</SectionTitle>
          <div className="space-y-1.5">
            {data.documentos_pendentes.map((d: any, i: number) => (
              <div key={i} className="flex items-center gap-2.5 rounded-xl bg-white/5 border border-white/10 px-3 py-2.5">
                <div className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                <span className="text-sm text-white/85">{typeof d === "string" ? d : d.nome || JSON.stringify(d)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ProbBadge({ p }: { p: string }) {
  const v = String(p).toLowerCase();
  const cfg = v.includes("alta") ? "bg-emerald-500/20 text-emerald-200 border-emerald-400/30"
    : v.includes("media") || v.includes("average") ? "bg-amber-500/20 text-amber-200 border-amber-400/30"
    : "bg-red-500/20 text-red-200 border-red-400/30";
  return <span className={`px-2.5 py-1 rounded-md border text-xs font-medium ${cfg}`}>Approval {p}</span>;
}

/* ---------- Raw JSON fallback ---------- */
function RawJson({ data }: { data: any }) {
  return (
    <details className="rounded-xl bg-white/5 border border-white/10 p-4">
      <summary className="cursor-pointer text-xs uppercase tracking-wider text-white/55">JSON Response</summary>
      <pre className="mt-3 text-xs text-white/75 whitespace-pre-wrap break-words leading-relaxed">
        {JSON.stringify(data, null, 2)}
      </pre>
    </details>
  );
}