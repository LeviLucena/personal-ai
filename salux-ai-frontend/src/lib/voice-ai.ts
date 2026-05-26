import { useCallback, useRef, useState } from "react";

const OPENAI_API_KEY = import.meta.env.VITE_OPENAI_API_KEY as string;

interface VoiceConfig {
  voice: "alloy" | "echo" | "fable" | "onyx" | "nova" | "shimmer";
  model: "tts-1" | "tts-1-hd";
  speed: number;
}

const DEFAULT_CONFIG: VoiceConfig = {
  voice: "nova",
  model: "tts-1",
  speed: 0.9,
};

const GOODBYE_MESSAGES = [
  "Até logo! Foi um prazer ajudar.",
  "Tchau! Quando precisar, é só chamar.",
  "Até mais! Cuide-se.",
  "Bom trabalho! Estou aqui se precisar.",
];

const WELCOME_MESSAGE = "Olá! Sou a Salux. Como posso ajudar você hoje?";

async function synthesizeSpeech(
  text: string,
  config: VoiceConfig = DEFAULT_CONFIG
): Promise<ArrayBuffer> {
  const response = await fetch("https://api.openai.com/v1/audio/speech", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: config.model,
      voice: config.voice,
      input: text,
      speed: config.speed,
      response_format: "mp3",
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`OpenAI TTS error: ${response.status} - ${error}`);
  }

  return response.arrayBuffer();
}

function playAudio(arrayBuffer: ArrayBuffer): Promise<void> {
  return new Promise((resolve, reject) => {
    const blob = new Blob([arrayBuffer], { type: "audio/mp3" });
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);

    audio.onended = () => {
      URL.revokeObjectURL(url);
      resolve();
    };

    audio.onerror = (e) => {
      URL.revokeObjectURL(url);
      reject(e);
    };

    audio.play().catch(reject);
  });
}

// Converts MP3 ArrayBuffer → PCM16 Uint8Array at 16 kHz mono (required by Simli)
async function mp3ToPcm16Bytes(arrayBuffer: ArrayBuffer): Promise<Uint8Array> {
  const tmpCtx = new AudioContext();
  const decoded = await tmpCtx.decodeAudioData(arrayBuffer.slice(0));
  await tmpCtx.close();

  const TARGET_RATE = 16000;
  const targetLength = Math.ceil(decoded.duration * TARGET_RATE);
  const offlineCtx = new OfflineAudioContext(1, targetLength, TARGET_RATE);
  const source = offlineCtx.createBufferSource();
  source.buffer = decoded;
  source.connect(offlineCtx.destination);
  source.start(0);
  const resampled = await offlineCtx.startRendering();

  const float32 = resampled.getChannelData(0);
  const int16 = new Int16Array(float32.length);
  for (let i = 0; i < float32.length; i++) {
    const s = Math.max(-1, Math.min(1, float32[i]));
    int16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }

  return new Uint8Array(int16.buffer);
}

function generateSummary(data: unknown, tag: string, _query: string): string {
  if (!data) return "";

  try {
    const d = data as Record<string, unknown>;

    if (tag === "WF-16") {
      const tipo = (d.dashboard as string) || "";
      const status = (d.status_operacional as string) || "";
      const alertas = (d.alertas_ativos as number) || 0;

      const criticas = ((d.unidades_criticas as string[]) || []).slice(0, 2);
      const unid = criticas.length ? ` Unidades críticas: ${criticas.join(", ")}.` : "";

      if (tipo === "EXECUTIVO") return `Dashboard executivo. Status ${status}. ${alertas} alertas ativos.${unid}`;
      if (tipo === "FINANCEIRO") return `Dashboard financeiro. ${d.glosas?.criticas || 0} glosas críticas. Valor em risco: ${d.glosas?.valor_total_em_risco || 0}.`;
      if (tipo === "REGULATORIO") return `Dashboard regulatório. ${d.fila?.criticas || 0} pacientes críticos na fila. ${d.fila?.sla_estourado || 0} com SLA estourado.`;
      if (tipo === "OPERACIONAL") {
        const p = d.gargalos?.previsoes || {};
        return `Dashboard operacional. ${p.pacientes_espera || 0} pacientes na fila, ${p.tempo_medio_espera_min || 0} minutos de espera, ${p.ocupacao_leitos_pct || 0} por cento de ocupação.${unid}`;
      }
      if (tipo === "AGENDA") {
        const ns = d.no_show || {};
        return `Dashboard agenda. ${ns.alto_risco || 0} pacientes com alto risco de não comparecimento. Total de ${ns.total_consultas || 0} consultas.`;
      }
      return `Dashboard ${tipo} carregado com sucesso.`;
    }

    if (tag === "WF-12") {
      const resposta = d.resposta as string;
      return (resposta || "Resposta recebida.").substring(0, 200);
    }

    if (tag === "WF-07") {
      const texto = d.texto_evolucao_sugerido as string;
      return (texto || "Documentação gerada.").substring(0, 200);
    }

    if (tag === "WF-08") {
      const just = d.justificativa_clinica as string;
      return (just || "Análise regulatória gerada.").substring(0, 200);
    }

    return "Resposta recebida.";
  } catch {
    return "Resposta recebida.";
  }
}

interface VoiceResponseOptions {
  // When provided, audio is converted to PCM16 and routed to this callback (Simli avatar).
  // The caller is responsible for waiting durationMs before marking speech as done.
  onAudioData?: (data: Uint8Array, durationMs: number) => void;
}

export function useVoiceResponse(options?: VoiceResponseOptions) {
  const [enabled, setEnabled] = useState(true);
  const [speaking, setSpeaking] = useState(false);
  const [muted, setMuted] = useState(false);
  const audioContextRef = useRef<AudioContext | null>(null);

  const speak = useCallback(
    async (text: string) => {
      if (!enabled || muted || !text) return;

      setSpeaking(true);
      try {
        const audioBuffer = await synthesizeSpeech(text);

        if (options?.onAudioData) {
          const pcm16 = await mp3ToPcm16Bytes(audioBuffer);
          const durationMs = (pcm16.byteLength / 2 / 16000) * 1000;
          options.onAudioData(pcm16, durationMs);
          // Wait for avatar to finish speaking before resolving
          await new Promise<void>((resolve) => setTimeout(resolve, durationMs + 400));
        } else {
          await playAudio(audioBuffer);
        }
      } catch (err) {
        console.error("Voice synthesis error:", err);
      } finally {
        setSpeaking(false);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [enabled, muted, options?.onAudioData]
  );

  const speakWelcome = useCallback(async () => {
    if (!enabled || muted) return;
    await speak(WELCOME_MESSAGE);
  }, [enabled, muted, speak]);

  const speakGoodbye = useCallback(async () => {
    if (!enabled || muted) return;
    const msg = GOODBYE_MESSAGES[Math.floor(Math.random() * GOODBYE_MESSAGES.length)];
    await speak(msg);
  }, [enabled, muted, speak]);

  const speakResponse = useCallback(
    async (data: unknown, tag: string, query: string) => {
      if (!enabled || muted) return;

      const summary = generateSummary(data, tag, query);
      if (summary) {
        await speak(summary);
      }
    },
    [enabled, muted, speak]
  );

  const toggleMute = useCallback(() => {
    setMuted((prev) => !prev);
  }, []);

  const toggleEnabled = useCallback(() => {
    setEnabled((prev) => !prev);
  }, []);

  return {
    enabled,
    speaking,
    muted,
    speak,
    speakWelcome,
    speakGoodbye,
    speakResponse,
    toggleMute,
    toggleEnabled,
  };
}

export type { VoiceConfig };
