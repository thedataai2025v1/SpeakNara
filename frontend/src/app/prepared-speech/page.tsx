"use client";

import { useCallback, useEffect, useState } from "react";

import AudioRecorder from "../components/AudioRecorder";
import FeedbackCard from "../components/FeedbackCard";
import type { FeedbackData } from "../components/FeedbackCard";
import Navbar from "../components/Navbar";

interface Topic {
  topic: string;
  keywords: string[];
  time_limit: number;
}


export default function PreparedSpeechPage() {
  const [phase, setPhase] = useState<"topic" | "record" | "analyzing" | "results">("topic");
  const [topic, setTopic] = useState<Topic | null>(null);
  const [preparedText, setPreparedText] = useState("");
  const [result, setResult] = useState<FeedbackData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchTopic = useCallback(async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/prepared-speech/generate");
      if (!res.ok) throw new Error("Failed to generate topic");
      const data: Topic = await res.json();
      setTopic(data);
      setPhase("topic");
    } catch (e: any) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    fetchTopic();
  }, [fetchTopic]);

  const handleStartRecording = () => {
    if (!preparedText.trim()) {
      setError("Please paste your prepared speech text before recording.");
      return;
    }
    setPhase("record");
  };

  const handleRecordingComplete = async (audioBlob: Blob) => {
    setPhase("analyzing");
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", audioBlob, "prepared-speech.webm");
      formData.append("mode", "prepared_speech");
      formData.append("metadata", JSON.stringify({
        topic: topic?.topic,
        keywords: topic?.keywords,
        prepared_text: preparedText,
      }));

      const res = await fetch("http://localhost:8000/api/v1/audio/upload", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
      const resJson = await res.json();
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
      setPhase("record");
    }
  };

  const handleNewSpeech = () => {
    setResult(null);
    setPreparedText("");
    fetchTopic();
  };

  if (error && phase === "topic") {
    return (
      <main className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 flex flex-col items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Error Loading Topic</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={fetchTopic}
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            Retry
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2 text-center">Prepared Speech</h1>
        <p className="text-center text-gray-600 mb-8">
          Paste your prepared speech, then record yourself delivering it.
        </p>

        {error && phase !== "topic" && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 text-red-700">
            <p className="font-medium">Error</p>
            <p>{error}</p>
            <button
              onClick={() => setPhase("topic")}
              className="mt-2 text-red-900 underline"
            >
              Go back
            </button>
          </div>
        )}

        {/* Topic display */}
        {phase === "topic" && topic && (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">📝 Speech Prompt</h2>
              <p className="text-gray-700 text-lg">{topic.topic}</p>
            </div>

            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Keywords to Include</h3>
              <div className="flex flex-wrap gap-2">
                {topic.keywords.map((kw, i) => (
                  <span key={i} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
                    {kw}
                  </span>
                ))}
              </div>
            </div>

            <div className="mb-6">
              <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
                <span>Time Limit</span>
                <span className="font-medium">{topic.time_limit}s ({Math.floor(topic.time_limit / 60)}m {topic.time_limit % 60}s)</span>
              </div>
            </div>

            {/* Prepared text input */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Paste Your Prepared Speech
              </label>
              <textarea
                className="w-full border border-gray-300 rounded-lg p-3 min-h-[200px] text-gray-800 focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-y"
                placeholder="Paste the speech you've prepared here..."
                value={preparedText}
                onChange={(e) => setPreparedText(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">
                {preparedText.trim().length > 0 ? `${preparedText.trim().length} characters` : 'Paste or type your prepared speech text here.'}
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleStartRecording}
                className="flex-1 bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                🎤 Ready to Record
              </button>
              <button
                onClick={fetchTopic}
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium text-gray-700"
              >
                New Topic
              </button>
            </div>
          </div>
        )}

        {/* Recording phase */}
        {phase === "record" && topic && (
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="mb-4">
              <p className="text-gray-700 font-medium">{topic.topic}</p>
            </div>
            <AudioRecorder
              timeLimit={topic.time_limit}
              onComplete={handleRecordingComplete}
              onError={(e) => { setError(e); setPhase("topic"); }}
            />
            <button
              onClick={() => setPhase("topic")}
              className="mt-4 text-gray-500 hover:text-gray-700 text-sm"
            >
              ← Back to prepare
            </button>
          </div>
        )}

        {/* Analyzing phase */}
        {phase === "analyzing" && (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <div className="animate-spin text-5xl mb-4">🔄</div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">Analyzing Your Speech</h2>
            <p className="text-gray-500">
              Transcribing and evaluating your delivery...
            </p>
          </div>
        )}

        {/* Results phase */}
        {phase === "results" && result && (
          <div className="space-y-6">
            <FeedbackCard data={result} />
            <div className="flex gap-3">
              <button
                onClick={handleNewSpeech}
                className="flex-1 bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
              >
                New Speech
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
