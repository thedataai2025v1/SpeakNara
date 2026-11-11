"use client";

import { useState } from "react";

import { FeedbackCard, type FeedbackData } from "../components/FeedbackCard";
import Navbar from "../components/Navbar";

export default function YouTubePage() {
  const [url, setUrl] = useState("");
  const [phase, setPhase] = useState<"input" | "analyzing" | "results">("input");
  const [result, setResult] = useState<FeedbackData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [videoTitle, setVideoTitle] = useState("");

  const handleAnalyze = async () => {
    if (!url.trim()) {
      setError("Please enter a YouTube URL.");
      return;
    }
    setPhase("analyzing");
    setError(null);
    try {
      // Step 1: Get transcript from YouTube
      const transcriptRes = await fetch("http://localhost:8000/api/v1/youtube/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      if (!transcriptRes.ok) {
        const errData = await transcriptRes.json();
        throw new Error(errData.detail || `Failed: ${transcriptRes.status}`);
      }
      const transcriptData = await transcriptRes.json();
      setVideoTitle(transcriptData.video_id || "YouTube video");

      // Step 2: Send transcript to /upload for full analysis
      const formData = new FormData();
      formData.append("mode", "youtube");
      formData.append("transcript", transcriptData.transcript);
      formData.append("metadata", JSON.stringify({
        url: url.trim(),
        video_id: transcriptData.video_id,
        word_count: transcriptData.word_count,
      }));

      const analysisRes = await fetch("http://localhost:8000/api/v1/audio/upload", {
        method: "POST",
        body: formData,
      });
      if (!analysisRes.ok) throw new Error(`Analysis failed: ${analysisRes.status}`);
      const resJson = await analysisRes.json();
      const mapped: FeedbackData = {
        score: resJson.feedback?.overall?.score ?? 0,
        score_rationale: resJson.feedback?.overall?.summary,
        wpm: resJson.metrics?.wpm,
        word_count: resJson.metrics?.words,
        duration: resJson.metrics?.duration,
        strengths: [],
        areas_for_improvement: [],
        specific_suggestions: [],
      };
      setResult(mapped);
      setPhase("results");
    } catch (e: any) {
      setError(e.message);
      setPhase("input");
    }
  };

  const handleNewAnalysis = () => {
    setResult(null);
    setUrl("");
    setVideoTitle("");
    setPhase("input");
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-red-50 to-orange-100">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2 text-center">YouTube Speech Analysis</h1>
        <p className="text-center text-gray-600 mb-8">
          Paste a YouTube URL to analyze any speech or presentation.
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 text-red-700">
            <p className="font-medium">Error</p>
            <p>{error}</p>
          </div>
        )}

        {phase === "input" && (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                YouTube URL
              </label>
              <input
                type="url"
                className="w-full border border-gray-300 rounded-lg px-4 py-3 text-gray-800 focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="https://www.youtube.com/watch?v=..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
              />
            </div>

            <button
              onClick={handleAnalyze}
              className="w-full bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 transition-colors font-medium"
            >
              ▶ Analyze Speech
            </button>

            <div className="mt-6 text-xs text-gray-400 text-center">
              Supports YouTube video URLs. The video will be transcribed and analyzed for speech quality.
            </div>
          </div>
        )}

        {phase === "analyzing" && (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <div className="animate-spin text-5xl mb-4">🔄</div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Analyzing YouTube Video</h2>
            <p className="text-gray-500">
              Transcribing and evaluating the speech...
            </p>
          </div>
        )}

        {phase === "results" && result && (
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <p className="text-sm text-gray-500 mb-1">Analyzed video</p>
              <p className="font-medium text-gray-800">
                {videoTitle ? `YouTube video (${videoTitle})` : "YouTube video"}
              </p>
              {url && (
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-red-600 hover:underline break-all"
                >
                  {url}
                </a>
              )}
            </div>
            <FeedbackCard data={result} />
            <div className="flex gap-3">
              <button
                onClick={handleNewAnalysis}
                className="flex-1 bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 transition-colors font-medium"
              >
                New Analysis
              </button>
              <a
                href="/"
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium text-gray-700 inline-block text-center"
              >
                Home
              </a>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
