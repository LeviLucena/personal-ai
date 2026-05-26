import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { exampleQueries } from "@/lib/personal-ai-workflows";

interface HelpModalProps {
  open: boolean;
  onClose: () => void;
  onPick: (text: string) => void;
}

export function HelpModal({ open, onClose, onPick }: HelpModalProps) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 bg-black/55 backdrop-blur-md flex items-center justify-center p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="w-full max-w-md rounded-3xl bg-[oklch(0.12_0.03_260/0.92)] backdrop-blur-2xl border border-white/12 shadow-2xl p-6"
            initial={{ scale: 0.94, y: 12, opacity: 0 }}
            animate={{ scale: 1, y: 0, opacity: 1 }}
            exit={{ scale: 0.94, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-[11px] uppercase tracking-[0.18em] text-blue-300 font-semibold">
                Examples
              </div>
              <button
                onClick={onClose}
                className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white/85 transition-colors"
                aria-label="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 max-h-[60vh] overflow-y-auto pr-1">
              {exampleQueries.map((ex) => (
                <button
                  key={ex.text}
                  onClick={() => { onPick(ex.text); onClose(); }}
                  className="w-full text-left rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 px-3.5 py-3 transition-all flex items-center justify-between gap-3 group"
                >
                  <span className="text-sm text-white/85 group-hover:text-white">{ex.text}</span>
                  <span className="text-[10px] uppercase tracking-wider text-blue-300 font-semibold shrink-0">{ex.tag}</span>
                </button>
              ))}
            </div>

            <p className="mt-4 text-[11px] text-white/45 leading-relaxed">
              The workflow is automatically detected from the message content. Tap the orb or the microphone to speak.
            </p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}