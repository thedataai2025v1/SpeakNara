"use client";

import React, { useState, useRef, useCallback, useEffect } from "react";
import { createClient } from "../../utils/supabase/client";

interface AudioRecorderProps {
  timeLimit?: number; // seconds, 0 = no limit
  onComplete?: (data: any) => void;
  onError?: (error: string) => void;
  className?: string;
}

type RecordingState = "idle" | "recording" | "uploading" | "error";

interface TimerState {
  minutes: number;
  seconds: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Icon Components ───────────────────────────────────────────────

const MicIcon: React.FC<{ size?: number; className?: string }> = ({
  size = 24,
  className = "",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={2}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
    <line x1="12" x2="12" y1="19" y2="23" />
    <line x1="8" x2="16" y1="23" y2="23" />
  </svg>
);

const StopIcon: React.FC<{ size?: number; className?: string }> = ({
  size = 24,
  className = "",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="currentColor"
    className={className}
  >
    <rect x="6" y="6" width="12" height="12" rx="2" />
  </svg>
);

const SpinnerIcon: React.FC<{ className?: string }> = ({ className = "" }) => (
  <svg
    className={`animate-spin ${className}`}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={2}
  >
    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
  </svg>
);

const WarningIcon: React.FC<{ size?: number; className?: string }> = ({
  size = 20,
  className = "",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={2}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
  >
    <path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
    <line x1="12" y1="9" x2="12" y2="13" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
);

// ─── Helper ─────────────────────────────────────────────────────────

function formatTimer(sec: number): TimerState {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return { minutes: m, seconds: s };
}

function pad(n: number): string {
  return n.toString().padStart(2, "0");
}

// ─── Component ──────────────────────────────────────────────────────

export default function AudioRecorder({
  timeLimit = 0,
  onComplete,
  onError,
  className = "",
}: AudioRecorderProps) {
  const [state, setState] = useState<RecordingState>("idle");
  const [elapsed, setElapsed] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timeLimitRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // ── Clean up timers on unmount ──
  useEffect(() => {
    return () => {
      stopTimers();
      stopStream();
    };
  }, []);

  function stopTimers() {
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = null;
    if (timeLimitRef.current) clearTimeout(timeLimitRef.current);
    timeLimitRef.current = null;
  }

  function stopStream() {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  }

  // ── Start recording ──
  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : "audio/ogg",
      });
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.start();
      setState("recording");
      setElapsed(0);
      setErrorMessage("");

      timerRef.current = setInterval(() => {
        setElapsed((prev) => prev + 1);
      }, 1000);

      if (timeLimit > 0) {
        timeLimitRef.current = setTimeout(() => {
          stopRecording();
        }, timeLimit * 1000);
      }
    } catch (err: any) {
      const msg = err.message || "Failed to access microphone";
      setState("error");
      setErrorMessage(msg);
      onError?.(msg);
    }
  }, [timeLimit, onError]);

  // ── Stop recording & upload ──
  const stopRecording = useCallback(async () => {
    stopTimers();

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      return new Promise<void>((resolve) => {
        mediaRecorderRef.current!.onstop = () => resolve();
        mediaRecorderRef.current!.stop();
      }).then(() => doUpload());
    } else {
      // Already stopped (time-limit path), upload existing chunks
      doUpload();
    }
  }, [onComplete, onError]);

  const doUpload = async () => {
    stopStream();

    const blob = new Blob(chunksRef.current, {
      type: mediaRecorderRef.current?.mimeType || "audio/webm",
    });

    if (blob.size === 0) {
      setState("error");
      setErrorMessage("Recording was empty");
      onError?.("Recording was empty");
      return;
    }

    setState("uploading");

    try {
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      const formData = new FormData();
      formData.append("file", blob, "recording.webm");

      const response = await fetch(`${API_URL}/api/v1/audio/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Upload failed (${response.status}): ${errText}`);
      }

      const data = await response.json();
      setState("idle");
      onComplete?.(data);
    } catch (err: any) {
      const msg = err.message || "Upload failed";
      setState("error");
      setErrorMessage(msg);
      onError?.(msg);
    }
  };

  // ── Button click handler ──
  const handleClick = () => {
    if (state === "idle" || state === "error") {
      startRecording();
    } else if (state === "recording") {
      stopRecording();
    }
  };

  // ── Render ──
  const timer = formatTimer(elapsed);

  return (
    <div className={`flex flex-col items-center gap-6 ${className}`}>
      {/* Pulsing ring wrapper – only shown while recording */}
      {state === "recording" && (
        <div className="absolute pointer-events-none">
          <span className="block h-28 w-28 rounded-full bg-red-400 opacity-30 animate-ping" />
        </div>
      )}

      {/* Timer display */}
      {(state === "recording" || state === "uploading") && (
        <div className="text-3xl font-mono font-bold text-purple-700 tabular-nums">
          {pad(timer.minutes)}:{pad(timer.seconds)}
        </div>
      )}

      {/* Record button */}
      <button
        onClick={handleClick}
        disabled={state === "uploading"}
        aria-label={
          state === "recording"
            ? "Stop recording"
            : state === "uploading"
              ? "Uploading"
              : state === "error"
                ? "Retry recording"
                : "Start recording"
        }
        className={`
          relative flex items-center justify-center rounded-full border-4
          transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-purple-300
          disabled:cursor-not-allowed
          h-20 w-20
          ${state === "recording"
            ? "bg-red-500 border-red-300 text-white shadow-lg shadow-red-200 scale-110 hover:bg-red-600"
            : state === "uploading"
              ? "bg-purple-200 border-purple-300 text-purple-500"
              : state === "error"
                ? "bg-amber-200 border-amber-300 text-amber-600 hover:bg-amber-300"
                : "bg-gray-200 border-gray-300 text-gray-500 hover:bg-gray-300 hover:text-gray-700"
          }
        `}
      >
        {state === "recording" && (
          <StopIcon size={28} />
        )}
        {state === "uploading" && (
          <SpinnerIcon className="w-7 h-7" />
        )}
        {state === "error" && (
          <WarningIcon size={24} className="text-amber-600" />
        )}
        {state === "idle" && (
          <MicIcon size={28} />
        )}
      </button>

      {/* Status text */}
      <div className="text-center min-h-[24px]">
        {state === "recording" && (
          <p className="text-sm font-medium text-red-500">
            {timeLimit > 0
              ? `Recording… ${pad(timer.minutes)}:${pad(timer.seconds)} / ${timeLimit}s`
              : "Recording…"}
          </p>
        )}
        {state === "uploading" && (
          <p className="text-sm font-medium text-purple-600">
            Uploading…
          </p>
        )}
        {state === "error" && (
          <p className="text-sm font-medium text-amber-600 flex items-center justify-center gap-1.5">
            <WarningIcon size={14} />
            {errorMessage}
          </p>
        )}
        {state === "idle" && (
          <p className="text-sm text-gray-500">
            Tap to start recording
          </p>
        )}
      </div>
    </div>
  );
}
