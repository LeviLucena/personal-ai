import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { HelpCircle, Volume2, VolumeX } from "lucide-react";
import { Orb } from "@/components/personal-ai/Orb";
import type { OrbState } from "@/components/personal-ai/Orb";
import { InputPill } from "@/components/personal-ai/InputPill";
import { ResponseSheet } from "@/components/personal-ai/ResponseSheet";
import { HelpModal } from "@/components/personal-ai/HelpModal";
import { detectWF, detectDashboardType, dashboardModes, workflows, type WorkflowKey } from "@/lib/personal-ai-workflows";
import { useSpeechRecognition } from "@/hooks/use-speech-recognition";
import { useVoiceResponse } from "@/lib/voice-ai";

export const Route = createFileRoute("/")({
  component: Index,
});

function Index() {
  const [text, setText] = useState("");
  const [orbState, setOrbState] = useState<OrbState>("idle");
  const [loading, setLoading] = useState(false);
  const [responseData, setResponseData] = useState<unknown>(null);
  const [responseTag, setResponseTag] = useState("");
  const [responseQuery, setResponseQuery] = useState("");
  const [sheetOpen, setSheetOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const [status, setStatus] = useState<{ text: string; tone: "ok" | "err" | "loading" | "info" } | null>(null);
  const [started, setStarted] = useState(false);
  const [modo, setModo] = useState("");

  const voice = useVoiceResponse({});

  // Welcome message fires only after user interaction (audio unlocked)
  useEffect(() => {
    if (!started) return;
    const timer = setTimeout(() => {
      voice.speakWelcome();
    }, 1500);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [started]);

  const handleStart = useCallback(async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      // mic denied — app still works via text input
    }
    setStarted(true);
  }, []);

  useEffect(() => { setModo(""); }, [detectDashboardType(text)]);

  const speech = useSpeechRecognition({
    lang: "pt-BR",
    onResult: (t) => {
      setText(t);
      setStatus({ text: "Transcription complete — review and send", tone: "ok" });
    },
    onError: (e) => setStatus({ text: `Voice error: ${e}`, tone: "err" }),
  });

  const avatarState: OrbState = speech.listening ? "listening" : loading ? "processing" : voice.speaking ? "speaking" : "idle";

  const submit = useCallback(async (override?: string) => {
    const q = (override ?? text).trim();
    if (!q || loading) return;
    const wf = workflows[detectWF(q)];
    setLoading(true);
    setOrbState("processing");
    setStatus({ text: `${wf.tag} — sending…`, tone: "loading" });
    try {
      const res = await fetch(wf.url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(wf.buildBody(q, "executivo", modo || undefined)),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const raw = await res.json();
      const data = wf.transformResponse(raw);
      setResponseData(data);
      setResponseTag(wf.tag);
      setResponseQuery(q);
      setSheetOpen(true);
      setStatus(null);
      setModo("");
      voice.speakResponse(data, wf.tag, q);
    } catch (err) {
      setStatus({ text: `Error: ${(err as Error).message}`, tone: "err" });
      setOrbState("idle");
    } finally {
      setLoading(false);
    }
  }, [text, loading, modo]);

  const handleDetach = useCallback(() => {
    const wk = detectWF(responseQuery) as WorkflowKey;
    localStorage.setItem("personal_ai_panel", JSON.stringify({
      data: responseData,
      tag: responseTag,
      query: responseQuery,
      comando: responseQuery,
      modo: modo,
      wfKey: wk,
    }));
    window.open("/panel", "_blank", "popup,width=440,height=700,top=80,left=80");
  }, [responseData, responseTag, responseQuery, modo]);

  const handleAvatarClick = () => {
    if (speech.supported) speech.toggle();
  };

  const greeting = sheetOpen ? null : (
    <motion.div
      key="greeting"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.5, delay: 0.15 }}
      className="text-center max-w-md mx-auto px-6"
    >
      <p className="text-[15px] text-slate-500 font-light tracking-wide">Hello</p>
      <h1 className="mt-2 text-[34px] sm:text-[42px] font-semibold leading-[1.1] tracking-tight text-slate-800">
        How can I help<br />you today?
      </h1>
    </motion.div>
  );

  return (
    <div
      className="relative min-h-screen w-full flex flex-col overflow-hidden"
      style={{ background: "var(--personal-ai-bg)" }}
    >
      {/* Soft noise / grain overlay for depth */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.035] mix-blend-overlay"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>\")",
        }}
      />

      {/* Top bar */}
      <header className="relative z-10 flex items-center justify-between px-5 sm:px-8 pt-5">
        <div className="text-[13px] font-semibold tracking-[0.2em] text-slate-600">PERSONAL AI</div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => voice.toggleMute()}
            aria-label={voice.muted ? "Enable voice" : "Disable voice"}
            className="w-9 h-9 rounded-full bg-black/[0.06] hover:bg-black/10 border border-black/[0.08] flex items-center justify-center text-slate-500 hover:text-slate-800 transition-all backdrop-blur-md"
          >
            {voice.muted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setHelpOpen(true)}
            aria-label="Examples"
            className="w-9 h-9 rounded-full bg-black/[0.06] hover:bg-black/10 border border-black/[0.08] flex items-center justify-center text-slate-500 hover:text-slate-800 transition-all backdrop-blur-md"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Center stage */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center gap-10 px-4 pb-40">
        <Orb
          state={avatarState}
          size={typeof window !== "undefined" && window.innerWidth < 480 ? 180 : 220}
          onClick={handleAvatarClick}
        />

        <AnimatePresence mode="wait">{greeting}</AnimatePresence>
      </main>

      {/* Floating input + status */}
      <div className="fixed bottom-0 inset-x-0 z-20 px-4 pb-6 pt-4 bg-gradient-to-t from-blue-100/70 to-transparent">
        <AnimatePresence>
          {status && (
            <motion.p
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`text-center text-xs mb-2.5 ${
                status.tone === "err" ? "text-red-400"
                  : status.tone === "ok" ? "text-emerald-600"
                  : status.tone === "loading" ? "text-blue-500"
                  : "text-slate-500"
              }`}
            >
              {status.text}
            </motion.p>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {detectWF(text) === "wf16" && text.trim() && (
            <motion.div
              key="modo-chips"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 6 }}
              transition={{ duration: 0.2 }}
              className="flex flex-wrap justify-center gap-2 mb-2.5 px-1"
            >
              <button
                onClick={() => setModo("")}
                className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${
                  modo === ""
                    ? "bg-slate-800 text-white border-slate-800"
                    : "bg-white/70 text-slate-500 border-slate-200 hover:border-slate-400"
                }`}
              >
                Complete
              </button>
              {dashboardModes[detectDashboardType(text)]?.map((chip) => (
                <button
                  key={chip.value}
                  onClick={() => setModo(modo === chip.value ? "" : chip.value)}
                  className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${
                    modo === chip.value
                      ? "bg-slate-800 text-white border-slate-800"
                      : "bg-white/70 text-slate-500 border-slate-200 hover:border-slate-400"
                  }`}
                >
                  {chip.label}
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        <InputPill
          value={text}
          onChange={setText}
          onSubmit={() => submit()}
          onVoiceToggle={speech.toggle}
          listening={speech.listening}
          loading={loading}
          placeholder={speech.listening ? "Listening…" : "Ask anything…"}
        />
      </div>

      <ResponseSheet
        open={sheetOpen}
        onClose={() => { setSheetOpen(false); setText(""); }}
        data={responseData}
        tag={responseTag}
        query={responseQuery}
        onDetach={responseTag === "WF-16" ? handleDetach : undefined}
      />

      <HelpModal
        open={helpOpen}
        onClose={() => setHelpOpen(false)}
        onPick={(t) => { setText(t); setTimeout(() => submit(t), 50); }}
      />

      {/* Initial interaction overlay — unlocks audio autoplay and requests mic */}
      <AnimatePresence>
        {!started && (
          <motion.div
            key="start-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, transition: { duration: 0.4 } }}
            className="fixed inset-0 z-50 flex items-center justify-center"
            style={{ backdropFilter: "blur(6px)", background: "oklch(0.97 0.01 252 / 0.75)" }}
          >
            <motion.button
              onClick={handleStart}
              initial={{ scale: 0.92, opacity: 0 }}
              animate={{ scale: 1, opacity: 1, transition: { delay: 0.15, duration: 0.35 } }}
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              className="px-10 py-4 rounded-full bg-slate-800 text-white text-[15px] font-medium tracking-wide shadow-lg hover:bg-slate-700 transition-colors"
            >
              Talk to Personal AI
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
