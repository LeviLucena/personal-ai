import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useRef, useState } from "react";
import { RefreshCw, X } from "lucide-react";
import { ResponseRenderer } from "@/components/salux/ResponseRenderer";
import { workflows, type WorkflowKey } from "@/lib/salux-workflows";

export const Route = createFileRoute("/panel")({
  component: Panel,
});

interface PanelPayload {
  data: unknown;
  tag: string;
  query: string;
  comando: string;
  modo: string;
  wfKey: WorkflowKey;
}

const INTERVALS = [
  { label: "30s", value: 30000 },
  { label: "1min", value: 60000 },
  { label: "5min", value: 300000 },
  { label: "Manual", value: 0 },
];

function Panel() {
  const [payload, setPayload] = useState<PanelPayload | null>(null);
  const [data, setData] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [pollInterval, setPollInterval] = useState(30000);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem("salux_panel");
    if (!raw) return;
    const p: PanelPayload = JSON.parse(raw);
    setPayload(p);
    setData(p.data);
    setLastUpdate(new Date());
  }, []);

  const refresh = useCallback(async () => {
    if (!payload) return;
    setLoading(true);
    try {
      const wf = workflows[payload.wfKey];
      const res = await fetch(wf.url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(wf.buildBody(payload.comando)),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const raw = await res.json();
      setData(wf.transformResponse(raw));
      setLastUpdate(new Date());
    } catch {
      // mantém dados anteriores
    } finally {
      setLoading(false);
    }
  }, [payload]);

  useEffect(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    if (pollInterval > 0 && payload) {
      timerRef.current = setInterval(refresh, pollInterval);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [pollInterval, refresh, payload]);

  if (!payload) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "oklch(0.12 0.03 260)" }}>
        <p className="text-white/50 text-sm">Nenhum painel destacado.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "oklch(0.12 0.03 260)" }}>
      {/* Header */}
      <div className="px-4 pt-4 pb-3 border-b border-white/10 flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="text-[10px] uppercase tracking-[0.15em] text-white/45 mb-1">{payload.tag}</div>
          <div className="text-[13px] text-white/80 truncate">{payload.query}</div>
        </div>
        <button
          onClick={() => window.close()}
          aria-label="Fechar"
          className="shrink-0 w-7 h-7 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white/70 transition-colors"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Polling controls */}
      <div className="px-4 py-2.5 border-b border-white/8 flex items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 flex-wrap">
          {INTERVALS.map((opt) => (
            <button
              key={opt.label}
              onClick={() => setPollInterval(opt.value)}
              className={`px-2.5 py-1 rounded-full text-[11px] font-medium border transition-all ${
                pollInterval === opt.value
                  ? "bg-white/15 text-white border-white/25"
                  : "text-white/45 border-white/10 hover:border-white/25"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {lastUpdate && (
            <span className="text-[10px] text-white/35 tabular-nums">
              {lastUpdate.toLocaleTimeString("pt-BR")}
            </span>
          )}
          <button
            onClick={refresh}
            disabled={loading}
            aria-label="Atualizar"
            className="w-7 h-7 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white/70 transition-colors disabled:opacity-40"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <ResponseRenderer data={data} tag={payload.tag} />
      </div>
    </div>
  );
}
