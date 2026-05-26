import { AnimatePresence, motion } from "framer-motion";
import { ExternalLink, X } from "lucide-react";
import { ResponseRenderer } from "./ResponseRenderer";

interface ResponseSheetProps {
  open: boolean;
  onClose: () => void;
  data: unknown;
  tag: string;
  query: string;
  onDetach?: () => void;
}

export function ResponseSheet({ open, onClose, data, tag, query, onDetach }: ResponseSheetProps) {
  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="fixed inset-x-0 bottom-0 z-50 max-h-[85vh] flex flex-col"
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            exit={{ y: "100%" }}
            transition={{ type: "spring", damping: 32, stiffness: 320 }}
          >
            <div className="mx-auto w-full max-w-2xl px-3 pb-3">
              <div className="rounded-t-[28px] sm:rounded-[28px] bg-[oklch(0.1_0.03_260/0.85)] backdrop-blur-2xl border border-white/12 shadow-[0_-20px_60px_rgba(0,0,0,0.5)] overflow-hidden flex flex-col max-h-[82vh]">
                {/* Drag handle */}
                <div className="flex justify-center pt-2.5 pb-1">
                  <div className="w-10 h-1 rounded-full bg-white/20" />
                </div>

                {/* Header — query bubble */}
                <div className="px-5 pt-3 pb-4 flex items-start justify-between gap-3 border-b border-white/8">
                  <div className="flex-1 min-w-0">
                    <div className="text-[10px] uppercase tracking-[0.15em] text-white/45 mb-1.5">{tag}</div>
                    <div className="text-[15px] text-white/90 line-clamp-2">{query}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    {onDetach && (
                      <button
                        onClick={onDetach}
                        aria-label="Destacar painel"
                        title="Abrir em janela flutuante"
                        className="shrink-0 w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white/85 transition-colors"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={onClose}
                      aria-label="Fechar"
                      className="shrink-0 w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white/85 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Body */}
                <div className="overflow-y-auto px-5 py-5 flex-1">
                  <ResponseRenderer data={data} tag={tag} />
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}