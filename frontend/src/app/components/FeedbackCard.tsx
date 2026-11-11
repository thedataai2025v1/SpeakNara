"use client";

import Link from "next/link";

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

interface FeedbackCardProps {
  data: FeedbackData;
  onRetry?: () => void;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function scoreColor(score: number): string {
  if (score >= 80) return "text-emerald-500";
  if (score >= 60) return "text-yellow-500";
  if (score >= 40) return "text-orange-500";
  return "text-red-500";
}

function scoreGradient(score: number): string {
  if (score >= 80)
    return "from-emerald-400 to-emerald-600";
  if (score >= 60)
    return "from-yellow-400 to-orange-500";
  if (score >= 40)
    return "from-orange-400 to-orange-600";
  return "from-red-400 to-red-600";
}

function scoreLabel(score: number): string {
  if (score >= 90) return "Excellent!";
  if (score >= 80) return "Great Job!";
  if (score >= 60) return "Good Effort!";
  if (score >= 40) return "Keep Practicing!";
  return "Needs Improvement";
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  if (m === 0) return `${s}s`;
  return `${m}m ${s}s`;
}

// ─── Inline SVG Icons ────────────────────────────────────────────────────────

function CheckCircle({ className = "" }: { className?: string }) {
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
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  );
}

function AlertTriangle({ className = "" }: { className?: string }) {
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
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

function Info({ className = "" }: { className?: string }) {
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
      <line x1="12" y1="16" x2="12" y2="12" />
      <line x1="12" y1="8" x2="12.01" y2="8" />
    </svg>
  );
}

function RotateCcw({ className = "" }: { className?: string }) {
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
      <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
      <path d="M3 3v5h5" />
    </svg>
  );
}

function Home({ className = "" }: { className?: string }) {
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
      <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  );
}

function Zap({ className = "" }: { className?: string }) {
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
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  );
}

function Hash({ className = "" }: { className?: string }) {
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
      <line x1="4" y1="9" x2="20" y2="9" />
      <line x1="4" y1="15" x2="20" y2="15" />
      <line x1="10" y1="3" x2="8" y2="21" />
      <line x1="16" y1="3" x2="14" y2="21" />
    </svg>
  );
}

function Clock({ className = "" }: { className?: string }) {
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

// ─── Circular Gauge ──────────────────────────────────────────────────────────

function ScoreGauge({ score, size = 160 }: { score: number; size?: number }) {
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = Math.min(Math.max(score / 100, 0), 1);
  const offset = circumference * (1 - progress);

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={12}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          className={`stroke-current ${scoreColor(score)}`}
          strokeWidth={12}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1s ease-out" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className={`text-5xl font-bold ${scoreColor(score)}`}
          style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
        >
          {score}
        </span>
        <span className="text-sm text-gray-500 font-medium">out of 100</span>
      </div>
    </div>
  );
}

// ─── Section Components ──────────────────────────────────────────────────────

function FeedbackSection({
  title,
  items,
  icon,
  iconColor,
  borderColor,
  bgColor,
}: {
  title: string;
  items: string[];
  icon: React.ReactNode;
  iconColor: string;
  borderColor: string;
  bgColor: string;
}) {
  if (!items || items.length === 0) return null;

  return (
    <div
      className={`rounded-xl border-l-4 ${borderColor} ${bgColor} p-4`}
    >
      <h3
        className={`flex items-center gap-2 text-sm font-semibold mb-3 ${iconColor}`}
        style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
      >
        {icon}
        {title}
      </h3>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li
            key={i}
            className="text-sm text-gray-700 flex items-start gap-2"
          >
            <span className={`mt-0.5 ${iconColor}`}>•</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

// ─── Main Component ──────────────────────────────────────────────────────────

export default function FeedbackCard({ data, onRetry }: FeedbackCardProps) {
  const score = data.score ?? 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-amber-50 flex items-center justify-center p-4">
      <div
        className="w-full max-w-2xl relative"
        style={{ fontFamily: "'Inter', sans-serif" }}
      >
        {/* Gradient border wrapper */}
        <div className="absolute -inset-1 bg-gradient-to-r from-purple-500 via-pink-500 to-amber-500 rounded-2xl opacity-70 blur-sm" />

        {/* Card */}
        <div className="relative bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-5">
            <h2
              className="text-2xl font-bold text-white text-center"
              style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
            >
              Speaking Analysis
            </h2>
            <p className="text-purple-200 text-center text-sm mt-1">
              {scoreLabel(score)}
            </p>
          </div>

          {/* Score Section */}
          <div className="flex flex-col items-center pt-8 pb-4">
            <ScoreGauge score={score} />
            {data.score_rationale && (
              <p className="mt-3 text-center text-sm text-gray-500 max-w-sm italic">
                {data.score_rationale}
              </p>
            )}
          </div>

          {/* Metrics Row */}
          <div className="px-6 pb-4">
            <div className="flex justify-center gap-4 sm:gap-8">
              <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-gray-50 border border-gray-100">
                <Zap className="w-4 h-4 text-purple-500" />
                <div>
                  <p className="text-lg font-bold text-gray-800">{data.wpm ?? "-"}</p>
                  <p className="text-xs text-gray-500">WPM</p>
                </div>
              </div>
              <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-gray-50 border border-gray-100">
                <Hash className="w-4 h-4 text-purple-500" />
                <div>
                  <p className="text-lg font-bold text-gray-800">{data.word_count ?? "-"}</p>
                  <p className="text-xs text-gray-500">Words</p>
                </div>
              </div>
              <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-gray-50 border border-gray-100">
                <Clock className="w-4 h-4 text-purple-500" />
                <div>
                  <p className="text-lg font-bold text-gray-800">
                    {data.duration ? formatDuration(data.duration) : "-"}
                  </p>
                  <p className="text-xs text-gray-500">Duration</p>
                </div>
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="mx-6 border-t border-gray-100" />

          {/* Feedback Sections */}
          <div className="px-6 py-6 space-y-4">
            <FeedbackSection
              title="Strengths"
              items={data.strengths ?? []}
              icon={<CheckCircle className="w-4 h-4" />}
              iconColor="text-emerald-600"
              borderColor="border-emerald-500"
              bgColor="bg-emerald-50/50"
            />

            <FeedbackSection
              title="Areas for Improvement"
              items={data.areas_for_improvement ?? []}
              icon={<AlertTriangle className="w-4 h-4" />}
              iconColor="text-amber-600"
              borderColor="border-amber-500"
              bgColor="bg-amber-50/50"
            />

            <FeedbackSection
              title="Suggestions"
              items={data.specific_suggestions ?? []}
              icon={<Info className="w-4 h-4" />}
              iconColor="text-blue-600"
              borderColor="border-blue-500"
              bgColor="bg-blue-50/50"
            />
          </div>

          {/* Divider */}
          <div className="mx-6 border-t border-gray-100" />

          {/* Actions */}
          <div className="px-6 py-5 flex flex-col sm:flex-row gap-3 justify-center">
            <button
              type="button"
              onClick={onRetry}
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 text-white font-semibold shadow-md hover:from-purple-700 hover:to-purple-800 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
            >
              <RotateCcw className="w-4 h-4" />
              Try Again
            </button>
            <Link
              href="/"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl border-2 border-gray-300 text-gray-700 font-semibold hover:bg-gray-50 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
            >
              <Home className="w-4 h-4" />
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export type { FeedbackData, FeedbackCardProps };
