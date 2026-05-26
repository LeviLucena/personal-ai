import { useCallback, useEffect, useRef, useState } from "react";

/* eslint-disable @typescript-eslint/no-explicit-any */
type SR = any;

interface Options {
  lang?: string;
  onResult?: (transcript: string) => void;
  onError?: (err: string) => void;
}

export function useSpeechRecognition({ lang = "pt-BR", onResult, onError }: Options = {}) {
  const [listening, setListening] = useState(false);
  const [supported, setSupported] = useState<boolean>(true);
  const recRef = useRef<SR>(null);

  useEffect(() => {
    const w = window as any;
    const SpeechRecognition = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (!SpeechRecognition) setSupported(false);
  }, []);

  const stop = useCallback(() => {
    try { recRef.current?.stop(); } catch { /* noop */ }
  }, []);

  const start = useCallback(() => {
    const w = window as any;
    const SpeechRecognition = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      onError?.("Speech not supported in this browser. Use Chrome or Edge.");
      return;
    }
    const rec = new SpeechRecognition();
    rec.lang = lang;
    rec.continuous = false;
    rec.interimResults = false;

    rec.onstart = () => setListening(true);
    rec.onresult = (e: any) => {
      const transcript = e.results[0][0].transcript;
      onResult?.(transcript);
    };
    rec.onerror = (e: any) => onError?.(String(e.error || "erro"));
    rec.onend = () => setListening(false);

    recRef.current = rec;
    rec.start();
  }, [lang, onResult, onError]);

  const toggle = useCallback(() => {
    if (listening) stop(); else start();
  }, [listening, start, stop]);

  return { listening, supported, start, stop, toggle };
}