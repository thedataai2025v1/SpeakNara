import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">SpeakNara</h1>
      <p className="text-xl text-gray-600 mb-12">
        AI-powered public speaking coach for Lak language
      </p>
      <div className="flex gap-4">
        <Link
          href="/login"
          className="rounded-md bg-blue-600 px-6 py-3 text-white hover:bg-blue-700"
        >
          Sign In
        </Link>
        <Link
          href="/register"
          className="rounded-md border border-gray-300 px-6 py-3 text-gray-700 hover:bg-gray-50"
        >
          Register
        </Link>
      </div>
    </main>
  );
}
