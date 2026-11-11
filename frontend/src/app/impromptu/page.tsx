"use client";

import { useState, useCallback } from "react";
import Navbar from "../components/Navbar";
import AudioRecorder from "../components/AudioRecorder";
import FeedbackCard from "../components/FeedbackCard";

// ─── Types ───────────────────────────────────────────────────────────────────

interface FeedbackData {
  score?: number;
  wpm?: number;
  word_count?: number;
  duration?: number;
  strengths?: string[];
  areas_for_improvement?: string[];
  specific_suggestions?: string[];
  score_rationale?: string;
}

// ─── Presets ─────────────────────────────────────────────────────────────────

const TIME_PRESETS = [60, 90, 120];
const DEFAULT_TIME = 90;

// ─── SVG Icons ───────────────────────────────────────────────────────────────

function MicIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3Z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" y1="19" x2="12" y2="23" />
      <line x1="8" y1="23" x2="16" y2="23" />
    </svg>
  );
}

function SparklesIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
    </svg>
  );
}

function ClockIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function ImpromptuPage() {
  const [topic, setTopic] = useState("");
  const [timeLimit, setTimeLimit] = useState(DEFAULT_TIME);
  const [feedback, setFeedback] = useState<FeedbackData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleComplete = useCallback((data: any) => {
    // The AudioRecorder uploads directly to /upload and returns feedback data
    setFeedback(data);
    setError(null);
  }, []);

  const handleError = useCallback((err: string) => {
    setError(err);
  }, []);

  const handleReset = useCallback(() => {
    setTopic("");
    setTimeLimit(DEFAULT_TIME);
    setFeedback(null);
    setError(null);
  }, []);

  // ── Show feedback when available ──

  if (feedback) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-violet-900 to-purple-900">
        <Navbar />
        <div className="flex items-center justify-center px-4 pb-12">
          <FeedbackCard data={feedback} onRetry={handleReset} />
        </div>
      </div>
    );
  }

  // ── Main form ──

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-violet-900 to-purple-900">
      <Navbar />

      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 py-12">
        <div className="w-full max-w-lg">
          {/* ── Decorative gradient border behind card ── */}
          <div
            className="absolute -inset-1 rounded-2xl opacity-50 blur-sm"
            style={{
              backgroundImage: "linear-gradient(to right, #c4b5fd, #fbbf24, #c4b5fd)",
            }}
          />

          <div className="relative bg-white rounded-2xl shadow-xl overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-violet-600 to-purple-600 px-8 pt-10 pb-8">
              <div className="flex items-center justify-center gap-3 mb-2">
                <MicIcon className="w-8 h-8 text-gold-300" />
                <h1
                  className="text-3xl font-bold text-white"
                  style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                >
                  Impromptu Speech
                </h1>
              </div>
              <p
                className="text-center text-purple-200 text-sm"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                Speak freely — no topic needed
              </p>
            </div>

            {/* Body */}
            <div
              className="px-8 py-6 space-y-8"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              {/* ── Optional topic ── */}
              <div>
                <label
                  htmlFor="topic"
                  className="block text-sm font-semibold text-gray-700 mb-2"
                >
                  <span className="flex items-center gap-2">
                    <SparklesIcon className="w-4 h-4 text-violet-500" />
                    Topic{" "}
                    <span className="font-normal text-gray-400">(optional)</span>
                  </span>
                </label>
                <input
                  id="topic"
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., My favourite hobby..."
                  className="w-full rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-800 placeholder-gray-400 focus:border-violet-400 focus:outline-none focus:ring-2 focus:ring-violet-300 transition-all"
                />
              </div>

              {/* ── Time limit selector ── */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  <span className="flex items-center gap-2">
                    <ClockIcon className="w-4 h-4 text-violet-500" />
                    Time Limit
                  </span>
                </label>
                <div className="flex gap-3">
                  {TIME_PRESETS.map((seconds) => {
                    const isSelected = timeLimit === seconds;
                    const label =
                      seconds === 60
                        ? "1 min"
                        : seconds === 90
                        ? "1m 30s"
                        : "2 min";

                    return (
                      <button
                        key={seconds}
                        type="button"
                        onClick={() => setTimeLimit(seconds)}
                        className={`flex-1 rounded-xl border-2 px-4 py-3 text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-violet-400 focus:ring-offset-1 ${
                          isSelected
                            ? "border-violet-500 bg-violet-50 text-violet-700 shadow-sm"
                            : "border-gray-200 bg-gray-50 text-gray-500 hover:border-violet-300 hover:text-violet-500"
                        }`}
                        aria-pressed={isSelected}
                      >
                        {label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* ── Error ── */}
              {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              {/* ── AudioRecorder ── */}
              <div>
                <AudioRecorder
                  timeLimit={timeLimit}
                  onComplete={handleComplete}
                  onError={handleError}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
