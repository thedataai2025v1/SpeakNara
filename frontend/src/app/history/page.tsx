"use client";

import Navbar from "../components/Navbar";
import SessionList from "../components/SessionList";

export default function HistoryPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-cyan-100">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2 text-center">History</h1>
        <p className="text-center text-gray-600 mb-8">
          Your past speech evaluations and progress.
        </p>
        <SessionList />
      </div>
    </main>
  );
}
