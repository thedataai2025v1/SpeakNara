"use client";

import { useEffect, useState } from "react";

interface SessionRecord {
  id: string;
  mode: string;
  topic: string;
  score: number;
  timestamp: string;
  wpm: number;
}

export default function SessionList() {
  const [sessions, setSessions] = useState<SessionRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("speaknara_sessions");
    if (stored) {
      try {
        setSessions(JSON.parse(stored));
      } catch {
        setSessions([]);
      }
    }
    setLoading(false);
  }, []);

  const addSession = (session: SessionRecord) => {
    const updated = [session, ...sessions].slice(0, 50);
    setSessions(updated);
    localStorage.setItem("speaknara_sessions", JSON.stringify(updated));
  };

  const clearHistory = () => {
    setSessions([]);
    localStorage.removeItem("speaknara_sessions");
  };

  const expose = () => {
    // Expose addSession globally for pages to call
    (window as any).__speaknaraSessions = { addSession };
    return { addSession };
  };

  useEffect(() => {
    expose();
  }, [sessions]);

  const getModeEmoji = (mode: string) => {
    switch (mode) {
      case "table_topics": return "🎯";
      case "storytelling": return "📖";
      case "prepared_speech": return "📝";
      case "youtube": return "▶️";
      case "impromptu": return "⚡";
      default: return "🎤";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600 bg-green-50";
    if (score >= 60) return "text-yellow-600 bg-yellow-50";
    return "text-red-600 bg-red-50";
  };

  if (loading) return null;

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800">📊 Recent Sessions</h2>
        {sessions.length > 0 && (
          <button
            onClick={clearHistory}
            className="text-xs text-red-500 hover:text-red-700"
          >
            Clear all
          </button>
        )}
      </div>

      {sessions.length === 0 ? (
        <p className="text-gray-400 text-sm text-center py-4">
          No sessions yet. Complete a speech evaluation to see it here.
        </p>
      ) : (
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {sessions.map((s) => (
            <div
              key={s.id}
              className="flex items-center gap-3 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
            >
              <span className="text-2xl">{getModeEmoji(s.mode)}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate">{s.topic}</p>
                <p className="text-xs text-gray-400">
                  {new Date(s.timestamp).toLocaleDateString()} {new Date(s.timestamp).toLocaleTimeString()}
                </p>
              </div>
              <div className={`px-2 py-1 rounded-full text-sm font-bold ${getScoreColor(s.score)}`}>
                {s.score}
              </div>
              <span className="text-xs text-gray-400 w-12 text-right">{s.wpm} wpm</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
