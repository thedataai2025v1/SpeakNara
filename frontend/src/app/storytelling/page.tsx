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

interface StoryPrompt {
  prompt: string;
  story_words: string[];
  time_limit: number;
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function StorytellingPage() {
  const [prompt, setPrompt] = useState<StoryPrompt | null>(null);
  const [feedback, setFeedback] = useState<FeedbackData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generatePrompt = useCallback(async () => {
    setLoading(true);
    setError(null);
    setFeedback(null);
    try {
      const res = await fetch("/api/v1/storytelling/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const data: StoryPrompt = await res.json();
      setPrompt(data);
    } catch (err: any) {
      setError(err.message || "Failed to generate prompt");
    } finally {
      setLoading(false);
    }
  }, []);

  const handleRecordingComplete = useCallback((data: FeedbackData) => {
    setFeedback(data);
  }, []);

  const handleRecordingError = useCallback((msg: string) => {
    setError(msg);
  }, []);

  const handleRetry = useCallback(() => {
    setPrompt(null);
    setFeedback(null);
    setError(null);
  }, []);

  return (
    <main className="flex min-h-screen flex-col bg-gradient-to-br from-indigo-900 via-violet-900 to-purple-900">
      {/* Navigation */}
      <Navbar />

      {/* Page Content */}
      <div className="flex flex-1 items-center justify-center px-4 py-24">
        <div className="w-full max-w-2xl">
          {/* Heading */}
          <div className="mb-8 text-center">
            <h1
              className="text-4xl font-bold tracking-tight"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              <span className="bg-gradient-to-r from-gold-300 via-gold-400 to-gold-500 bg-clip-text text-transparent">
                Storytelling
              </span>
            </h1>
            <p
              className="mt-3 text-lg text-purple-200"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              Weave a compelling story around a prompt
            </p>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
              {error}
            </div>
          )}

          {/* Step 1 — Generate Prompt */}
          {!prompt && !feedback && (
            <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur-sm">
              <p
                className="mb-6 text-purple-200"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                Click the button below to receive a unique storytelling prompt.
                You&rsquo;ll be given story words to include and a time limit.
              </p>
              <button
                onClick={generatePrompt}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 px-8 py-3 text-base font-semibold text-indigo-950 shadow-lg shadow-gold-500/20 transition-all duration-200 hover:from-gold-400 hover:to-gold-500 hover:shadow-gold-500/40 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                {loading ? (
                  <>
                    <svg
                      className="h-5 w-5 animate-spin"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                    </svg>
                    Generating&hellip;
                  </>
                ) : (
                  "Generate Prompt"
                )}
              </button>
            </div>
          )}

          {/* Step 2 — Prompt + Story Words + Recorder */}
          {prompt && !feedback && (
            <div className="space-y-6">
              {/* Prompt Card */}
              <div className="rounded-2xl border border-white/10 bg-white/5 p-8 backdrop-blur-sm">
                <h2
                  className="text-sm font-medium uppercase tracking-widest text-gold-400"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  Your Prompt
                </h2>
                <p
                  className="mt-3 text-xl leading-relaxed text-white"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {prompt.prompt}
                </p>
              </div>

              {/* Story Words */}
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
                <h2
                  className="text-sm font-medium uppercase tracking-widest text-gold-400"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  Your Story Words
                </h2>
                <div className="mt-3 flex flex-wrap gap-2">
                  {prompt.story_words.map((word) => (
                    <span
                      key={word}
                      className="rounded-full bg-gradient-to-r from-lilac-500 to-lilac-600 px-3 py-1 text-sm font-medium text-white shadow-sm"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {word}
                    </span>
                  ))}
                </div>
              </div>

              {/* Time Limit */}
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
                <h2
                  className="text-sm font-medium uppercase tracking-widest text-gold-400"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  Time Limit
                </h2>
                <p
                  className="mt-2 text-lg font-semibold text-white"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {prompt.time_limit} seconds
                </p>
              </div>

              {/* Recorder */}
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm">
                <AudioRecorder
                  timeLimit={prompt.time_limit}
                  onComplete={handleRecordingComplete}
                  onError={handleRecordingError}
                />
              </div>
            </div>
          )}

          {/* Step 3 — Feedback */}
          {feedback && (
            <div className="space-y-6">
              <FeedbackCard data={feedback} onRetry={handleRetry} />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
