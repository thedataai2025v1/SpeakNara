"use client";

import { useState } from "react";
import Navbar from "../components/Navbar";
import AudioRecorder from "../components/AudioRecorder";
import FeedbackCard from "../components/FeedbackCard";

interface GeneratedTopic {
  topic: string;
  keywords: string[];
  time_limit: number;
}

type PageState = "idle" | "loading" | "ready" | "feedback" | "error";

export default function TableTopicsPage() {
  const [state, setState] = useState<PageState>("idle");
  const [topic, setTopic] = useState<GeneratedTopic | null>(null);
  const [feedbackData, setFeedbackData] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState("");

  async function generateTopic() {
    setState("loading");
    setErrorMessage("");
    try {
      const res = await fetch("/api/v1/table-topics/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) throw new Error(`Server responded ${res.status}`);
      const data: GeneratedTopic = await res.json();
      setTopic(data);
      setState("ready");
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to generate a topic. Please try again.");
      setState("error");
    }
  }

  function handleRecordingComplete(data: any) {
    setFeedbackData(data);
    setState("feedback");
  }

  function handleRecordingError(error: string) {
    setErrorMessage(error);
    setState("error");
  }

  function resetPage() {
    setState("idle");
    setTopic(null);
    setFeedbackData(null);
    setErrorMessage("");
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-900 via-violet-900 to-purple-900">
      <Navbar />

      <div className="flex items-center justify-center min-h-screen px-4 pt-20">
        <div className="w-full max-w-2xl">
          {/* ── State: Idle / Loading / Error ─────────────────── */}
          {(state === "idle" || state === "loading" || state === "error") && (
            <div className="rounded-2xl bg-white/10 backdrop-blur-lg border border-white/20 shadow-xl p-8 sm:p-12 text-center">
              <h1
                className="text-4xl sm:text-5xl font-bold mb-4 font-[Plus_Jakarta_Sans]"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                Table Topics
              </h1>
              {state === "idle" && (
                <p
                  className="text-lg sm:text-xl text-purple-200 mb-10 font-[Inter]"
                  style={{ fontFamily: "Inter, sans-serif" }}
                >
                  Pick a random topic and speak on the spot
                </p>
              )}

              {state === "loading" ? (
                <div className="flex flex-col items-center gap-4 py-8">
                  <svg
                    className="animate-spin h-10 w-10 text-gold-400"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={2}
                  >
                    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                  </svg>
                  <p className="text-purple-200 text-lg font-[Inter]"
                    style={{ fontFamily: "Inter, sans-serif" }}>
                    Generating a topic…
                  </p>
                </div>
              ) : (
                <button
                  onClick={generateTopic}
                  className="rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 px-8 py-4 text-lg font-semibold text-indigo-950 hover:from-gold-400 hover:to-gold-500 shadow-lg shadow-gold-500/20 hover:shadow-gold-500/40 transition-all duration-200"
                >
                  {state === "error" ? "Retry" : "Generate Topic"}
                </button>
              )}

              {state === "error" && (
                <div className="mt-6 rounded-lg bg-red-500/20 border border-red-400/40 p-4 text-red-200 text-sm font-[Inter]"
                  style={{ fontFamily: "Inter, sans-serif" }}>
                  {errorMessage}
                </div>
              )}
            </div>
          )}


          {/* ── State: Ready (topic generated, waiting for recording) ── */}
          {state === "ready" && topic && (
            <div className="rounded-2xl bg-white/10 backdrop-blur-lg border border-white/20 shadow-xl p-8 sm:p-12">
              <h1
                className="text-4xl sm:text-5xl font-bold mb-2 text-center font-[Plus_Jakarta_Sans]"
                style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                Table Topics
              </h1>
              <p
                className="text-center text-purple-200 mb-8 font-[Inter]"
                style={{ fontFamily: "Inter, sans-serif" }}
              >
                Speak for {topic.time_limit} seconds
              </p>

              {/* Topic */}
              <div className="text-center mb-6">
                <h2
                  className="text-2xl sm:text-3xl font-semibold text-gold-300 mb-4 font-[Plus_Jakarta_Sans]"
                  style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
                >
                  {topic.topic}
                </h2>

                {/* Keyword chips */}
                {topic.keywords && topic.keywords.length > 0 && (
                  <div className="flex flex-wrap justify-center gap-2 mb-6">
                    {topic.keywords.map((kw, i) => (
                      <span
                        key={i}
                        className="inline-block rounded-full bg-lilac-500/30 border border-lilac-400/40 px-3 py-1 text-sm text-lilac-200 font-[Inter]"
                        style={{ fontFamily: "Inter, sans-serif" }}
                      >
                        {kw}
                      </span>
                    ))}
                  </div>
                )}

                {/* Time limit */}
                <p
                  className="text-lg text-purple-300 font-[Inter]"
                  style={{ fontFamily: "Inter, sans-serif" }}
                >
                  Time limit: {topic.time_limit} seconds
                </p>
              </div>

              <div className="border-t border-white/10 my-6" />

              {/* AudioRecorder */}
              <AudioRecorder
                timeLimit={topic.time_limit}
                onComplete={handleRecordingComplete}
                onError={handleRecordingError}
              />
            </div>
          )}

          {/* ── State: Feedback ──────────────────────────────── */}
          {state === "feedback" && feedbackData && (
            <div className="rounded-2xl bg-white/10 backdrop-blur-lg border border-white/20 shadow-xl p-8 sm:p-12">
              <FeedbackCard
                data={feedbackData}
                onRetry={resetPage}
              />
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
