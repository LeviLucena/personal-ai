import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";
import { motion } from "framer-motion";
import { SimliClient, generateSimliSessionToken, generateIceServers } from "simli-client";
import type { OrbState } from "./Orb";

export interface AvatarStreamHandle {
  sendAudio(data: Uint8Array): void;
  unlockAudio(): Promise<void>;
}

interface AvatarStreamProps {
  state: OrbState;
  size?: number;
  onClick?: () => void;
}

const PALETTE: Record<OrbState, { glow: string; ring: string }> = {
  idle:       { glow: "oklch(0.65 0.22 245 / 0.3)",  ring: "oklch(0.65 0.22 245 / 0.55)" },
  listening:  { glow: "oklch(0.7 0.2 210 / 0.4)",    ring: "oklch(0.7 0.2 210 / 0.7)"    },
  processing: { glow: "oklch(0.65 0.25 280 / 0.4)",  ring: "oklch(0.65 0.25 280 / 0.7)"  },
  speaking:   { glow: "oklch(0.7 0.22 235 / 0.4)",   ring: "oklch(0.7 0.22 235 / 0.85)"  },
};

export const AvatarStream = forwardRef<AvatarStreamHandle, AvatarStreamProps>(
  ({ state, size = 220, onClick }, ref) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const audioRef = useRef<HTMLAudioElement>(null);
    const clientRef = useRef<SimliClient | null>(null);
    const [connected, setConnected] = useState(false);
    const [videoReady, setVideoReady] = useState(false);
    // Incrementing this triggers a full Simli reconnect (used when session times out)
    const [reconnectKey, setReconnectKey] = useState(0);

    useImperativeHandle(ref, () => ({
      sendAudio(data: Uint8Array) {
        const client = clientRef.current;
        if (!client || !connected) return;
        const CHUNK = 6000;
        for (let i = 0; i < data.byteLength; i += CHUNK) {
          client.sendAudioData(data.slice(i, i + CHUNK));
        }
      },
      unlockAudio() {
        return audioRef.current?.play() ?? Promise.resolve();
      },
    }));

    // Resume video playback when tab regains focus (Scenario A: tab switching)
    useEffect(() => {
      const handleVisibility = () => {
        if (document.visibilityState === "visible" && videoRef.current) {
          videoRef.current.play().catch(() => {});
        }
      };
      document.addEventListener("visibilitychange", handleVisibility);
      return () => document.removeEventListener("visibilitychange", handleVisibility);
    }, []);

    // Simli session lifecycle — reruns on reconnectKey change
    useEffect(() => {
      if (!videoRef.current || !audioRef.current) return;
      const videoEl = videoRef.current;
      const audioEl = audioRef.current;
      let client: SimliClient | null = null;
      let mounted = true;

      setConnected(false);
      setVideoReady(false);

      async function init() {
        try {
          const apiKey = import.meta.env.VITE_SIMLI_API_KEY as string;
          const faceId = import.meta.env.VITE_SIMLI_FACE_ID as string;

          const [{ session_token }, iceServers] = await Promise.all([
            generateSimliSessionToken({
              apiKey,
              config: { faceId, handleSilence: true, maxSessionLength: 3600, maxIdleTime: 300 },
            }),
            generateIceServers(apiKey),
          ]);

          if (!mounted) return;

          client = new SimliClient(session_token, videoEl, audioEl, iceServers);
          clientRef.current = client;

          client.on("start", () => {
            if (mounted) {
              setConnected(true);
              videoEl.play().catch(() => {});
              audioEl.play().catch(() => {});
            }
          });
          client.on("stop", () => {
            if (!mounted) return;
            setConnected(false);
            setVideoReady(false);
            // Session timed out server-side — reconnect automatically
            setReconnectKey((k) => k + 1);
          });
          client.on("error", (detail) => {
            console.error("Simli error:", detail);
          });

          await client.start();
        } catch (err) {
          console.error("Simli init failed:", err);
        }
      }

      init();

      return () => {
        mounted = false;
        client?.stop();
        clientRef.current = null;
      };
    }, [reconnectKey]);

    const palette = PALETTE[state];
    const pulseDuration =
      state === "listening" ? 1.2 :
      state === "speaking"  ? 0.85 :
      state === "processing" ? 1.0 : 3.0;

    return (
      <button
        onClick={onClick}
        aria-label="Avatar Personal AI"
        className="relative cursor-pointer bg-transparent border-0 p-0 outline-none focus-visible:ring-2 focus-visible:ring-white/30 rounded-full"
        style={{ width: size, height: size }}
      >
        <motion.div
          className="absolute inset-[-12%] rounded-full pointer-events-none"
          style={{
            background: `radial-gradient(circle, ${palette.glow} 0%, transparent 65%)`,
            filter: "blur(20px)",
          }}
          animate={{ opacity: state === "idle" ? [0.4, 0.7, 0.4] : [0.6, 1, 0.6] }}
          transition={{ duration: pulseDuration, repeat: Infinity, ease: "easeInOut" }}
        />

        <motion.div
          className="absolute inset-0 rounded-full pointer-events-none"
          style={{
            boxShadow: `0 0 0 ${state === "speaking" ? 3 : 2}px ${palette.ring}, 0 0 28px ${palette.glow}`,
          }}
          animate={{
            opacity: state === "idle" ? [0.5, 0.85, 0.5] : [0.7, 1, 0.7],
            scale: state === "speaking" ? [1, 1.018, 1] : [1, 1.006, 1],
          }}
          transition={{ duration: pulseDuration, repeat: Infinity, ease: "easeInOut" }}
        />

        <div
          className="relative w-full h-full rounded-full overflow-hidden"
          style={{ background: "oklch(0.1 0.05 250)" }}
        >
          {/* muted required for autoplay; audio comes from <audio> element */}
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            onCanPlay={() => setVideoReady(true)}
            className="w-full h-full object-cover"
          />

          {!videoReady && (
            <motion.div
              className="absolute inset-0 flex items-center justify-center"
              style={{ background: "oklch(0.12 0.06 250 / 0.88)" }}
              animate={{ opacity: [0.75, 1, 0.75] }}
              transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
            >
              <div className="w-8 h-8 rounded-full border-2 border-white/20 border-t-white/70 animate-spin" />
            </motion.div>
          )}
        </div>

        <audio ref={audioRef} autoPlay className="hidden" />
      </button>
    );
  }
);

AvatarStream.displayName = "AvatarStream";
