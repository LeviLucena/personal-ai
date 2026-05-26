import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Mic, MicOff, ArrowUp, Loader2 } from "lucide-react";

interface InputPillProps {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  onVoiceToggle: () => void;
  listening: boolean;
  loading: boolean;
  placeholder?: string;
}

export function InputPill({
  value, onChange, onSubmit, onVoiceToggle, listening, loading, placeholder,
}: InputPillProps) {
  const taRef = useRef<HTMLTextAreaElement>(null);
  const [focused, setFocused] = useState(false);

  // Auto-resize textarea
  useEffect(() => {
    const ta = taRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`;
  }, [value]);

  const handleKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !loading) onSubmit();
    }
  };

  return (
    <motion.div
      initial={{ y: 30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="w-full max-w-[640px] mx-auto"
    >
      <div
        className={`relative flex items-end gap-2 rounded-[28px] px-5 py-3 backdrop-blur-2xl transition-all duration-300 ${
          focused ? "bg-white/90 border-black/12" : "bg-white/70 border-black/[0.07]"
        } border shadow-[0_8px_32px_rgba(100,120,200,0.12),inset_0_1px_0_rgba(255,255,255,0.9)]`}
      >
        <textarea
          ref={taRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKey}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          rows={1}
          placeholder={placeholder ?? "Pergunte qualquer coisa…"}
          className="flex-1 bg-transparent text-slate-800 placeholder:text-slate-400 text-[15px] leading-6 outline-none resize-none py-1.5 max-h-40 font-normal"
        />

        <button
          type="button"
          onClick={onVoiceToggle}
          aria-label={listening ? "Parar de ouvir" : "Falar"}
          className={`shrink-0 w-9 h-9 rounded-full flex items-center justify-center transition-all ${
            listening
              ? "bg-red-500/90 text-white shadow-[0_0_20px_rgba(239,68,68,0.5)]"
              : "bg-black/[0.07] text-slate-500 hover:bg-black/12"
          }`}
        >
          {listening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
        </button>

        {value.trim() && (
          <motion.button
            type="button"
            onClick={onSubmit}
            disabled={loading}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            aria-label="Enviar"
            className="shrink-0 w-9 h-9 rounded-full bg-slate-800 text-white flex items-center justify-center hover:bg-slate-700 disabled:opacity-50 transition-all"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowUp className="w-4 h-4" strokeWidth={2.5} />}
          </motion.button>
        )}
      </div>
    </motion.div>
  );
}