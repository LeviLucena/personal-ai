import { motion } from "framer-motion";

export type OrbState = "idle" | "listening" | "processing" | "speaking";

interface OrbProps {
  state: OrbState;
  size?: number;
  onClick?: () => void;
}

/**
 * Orb estilo Apple Intelligence — esfera luminosa com gradiente animado.
 * Estados visuais distintos para idle / listening / processing / speaking.
 */
export function Orb({ state, size = 220, onClick }: OrbProps) {
  const palette = {
    idle: {
      core: "oklch(0.85 0.15 240)",
      mid: "oklch(0.55 0.22 250)",
      edge: "oklch(0.18 0.12 265)",
      glow: "oklch(0.65 0.22 245 / 0.55)",
    },
    listening: {
      core: "oklch(0.92 0.18 195)",
      mid: "oklch(0.65 0.2 210)",
      edge: "oklch(0.2 0.1 240)",
      glow: "oklch(0.7 0.2 210 / 0.6)",
    },
    processing: {
      core: "oklch(0.85 0.2 290)",
      mid: "oklch(0.6 0.25 280)",
      edge: "oklch(0.2 0.15 270)",
      glow: "oklch(0.65 0.25 280 / 0.6)",
    },
    speaking: {
      core: "oklch(0.95 0.2 75)",
      mid: "oklch(0.72 0.26 58)",
      edge: "oklch(0.28 0.16 45)",
      glow: "oklch(0.78 0.28 65 / 0.8)",
    },
  }[state];

  const scale =
    state === "listening" ? [1, 1.04, 1] :
    state === "speaking" ? [1, 1.06, 0.98, 1.04, 1] :
    state === "processing" ? [1, 1.02, 1] :
    [1, 1.015, 1];

  const duration =
    state === "listening" ? 1.4 :
    state === "speaking" ? 0.9 :
    state === "processing" ? 1.2 :
    3.6;

  return (
    <button
      onClick={onClick}
      aria-label="Personal AI orb"
      className="relative cursor-pointer bg-transparent border-0 p-0 outline-none focus-visible:ring-2 focus-visible:ring-white/30 rounded-full"
      style={{ width: size, height: size }}
    >
      {/* Outer halo */}
      <motion.div
        className="absolute inset-[-12%] rounded-full pointer-events-none"
        style={{
          background: `radial-gradient(circle, ${palette.glow} 0%, transparent 65%)`,
          filter: "blur(20px)",
        }}
        animate={{ opacity: state === "idle" ? [0.5, 0.75, 0.5] : state === "speaking" ? [0.7, 1, 0.5, 1, 0.7] : [0.7, 1, 0.7] }}
        transition={{ duration, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Sphere */}
      <motion.div
        className="relative w-full h-full rounded-full overflow-hidden"
        animate={{ scale, rotate: state === "processing" ? [0, 360] : 0 }}
        transition={{
          scale: { duration, repeat: Infinity, ease: "easeInOut" },
          rotate: { duration: 4, repeat: Infinity, ease: "linear" },
        }}
        style={{
          background: `radial-gradient(circle at 35% 32%, ${palette.core} 0%, ${palette.mid} 38%, ${palette.edge} 78%, oklch(0.05 0.02 260) 100%)`,
          boxShadow: `0 0 60px ${palette.glow}, inset -20px -30px 60px oklch(0.05 0.05 260 / 0.6), inset 18px 20px 50px oklch(1 0 0 / 0.12)`,
        }}
      >
        {/* Internal swirl 1 */}
        <motion.div
          className="absolute inset-[8%] rounded-full opacity-70 mix-blend-screen"
          style={{
            background: `conic-gradient(from 0deg, transparent 0%, ${palette.core} 25%, transparent 50%, ${palette.mid} 75%, transparent 100%)`,
            filter: "blur(14px)",
          }}
          animate={{ rotate: 360 }}
          transition={{ duration: state === "processing" ? 2 : 8, repeat: Infinity, ease: "linear" }}
        />
        {/* Internal swirl 2 (reverse) */}
        <motion.div
          className="absolute inset-[18%] rounded-full opacity-60 mix-blend-screen"
          style={{
            background: `conic-gradient(from 180deg, transparent, ${palette.core}, transparent, ${palette.mid}, transparent)`,
            filter: "blur(10px)",
          }}
          animate={{ rotate: -360 }}
          transition={{ duration: state === "processing" ? 1.5 : 12, repeat: Infinity, ease: "linear" }}
        />
        {/* Specular highlight */}
        <div
          className="absolute rounded-full pointer-events-none"
          style={{
            top: "10%",
            left: "20%",
            width: "40%",
            height: "30%",
            background: "radial-gradient(ellipse, oklch(1 0 0 / 0.55) 0%, transparent 70%)",
            filter: "blur(8px)",
          }}
        />
      </motion.div>
    </button>
  );
}