"use client";

import { createClient } from "../../utils/supabase/client";
import Link from "next/link";
import { useEffect, useState } from "react";

interface UserSession {
  email: string | undefined;
  isLoggedIn: boolean;
}

interface NavLink {
  href: string;
  label: string;
  emoji: string;
}

export default function Navbar() {
  const [session, setSession] = useState<UserSession>({
    email: undefined,
    isLoggedIn: false,
  });
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const supabase = createClient();

    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        setSession({
          email: session.user.email,
          isLoggedIn: true,
        });
      }
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        setSession({
          email: session.user.email,
          isLoggedIn: true,
        });
      } else {
        setSession({
          email: undefined,
          isLoggedIn: false,
        });
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleSignOut = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    setSession({ email: undefined, isLoggedIn: false });
  };

  const navLinks: NavLink[] = [
    { href: "/table-topics", label: "Table Topics", emoji: "🎤" },
    { href: "/storytelling", label: "Storytelling", emoji: "📖" },
    { href: "/impromptu", label: "Impromptu", emoji: "✨" },
    { href: "/prepared-speech", label: "Prepared Speech", emoji: "🎯" },
  ];

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled || mobileOpen
          ? "bg-gradient-to-r from-indigo-900 via-violet-900 to-purple-900/95 backdrop-blur-lg shadow-lg shadow-purple-900/20"
          : "bg-gradient-to-r from-indigo-900 via-violet-900 to-purple-900"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo / Brand */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center shadow-md shadow-gold-500/30 group-hover:shadow-gold-500/50 transition-shadow text-lg">
              🎤
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-gold-300 via-gold-400 to-gold-500 bg-clip-text text-transparent">
              SpeakNara
            </span>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm text-purple-200 hover:text-gold-300 hover:bg-white/10 transition-all duration-200"
              >
                <span>{link.emoji}</span>
                <span>{link.label}</span>
              </Link>
            ))}

            <div className="w-px h-6 bg-white/20 mx-2" />

            {session.isLoggedIn ? (
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/10 text-sm text-purple-200">
                  <span className="text-gold-400">👤</span>
                  <span className="truncate max-w-[140px]">
                    {session.email}
                  </span>
                </div>
                <button
                  onClick={handleSignOut}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm text-purple-200 hover:text-red-300 hover:bg-white/10 transition-all duration-200"
                >
                  <span>🚪</span>
                  <span>Sign Out</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  href="/login"
                  className="px-4 py-2 rounded-lg text-sm text-purple-200 hover:text-gold-300 hover:bg-white/10 transition-all duration-200"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 rounded-lg text-sm bg-gradient-to-r from-gold-500 to-gold-600 text-indigo-950 font-semibold hover:from-gold-400 hover:to-gold-500 shadow-md shadow-gold-500/20 hover:shadow-gold-500/40 transition-all duration-200"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="p-2 rounded-lg text-purple-200 hover:bg-white/10 transition-colors"
              aria-label="Toggle menu"
            >
              {mobileOpen ? "✕" : "☰"}
            </button>
          </div>
        </div>

        {/* Mobile Menu Dropdown */}
        {mobileOpen && (
          <div className="md:hidden pb-4 border-t border-white/10 pt-3 space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm text-purple-200 hover:text-gold-300 hover:bg-white/10 transition-all duration-200"
              >
                <span>{link.emoji}</span>
                <span>{link.label}</span>
              </Link>
            ))}

            <div className="w-full h-px bg-white/10 my-2" />

            {session.isLoggedIn ? (
              <div className="space-y-1">
                <div className="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-white/10 text-sm text-purple-200">
                  <span className="text-gold-400">👤</span>
                  <span className="truncate">{session.email}</span>
                </div>
                <button
                  onClick={handleSignOut}
                  className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm text-purple-200 hover:text-red-300 hover:bg-white/10 transition-all duration-200"
                >
                  <span>🚪</span>
                  <span>Sign Out</span>
                </button>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                <Link
                  href="/login"
                  onClick={() => setMobileOpen(false)}
                  className="px-3 py-2.5 rounded-lg text-sm text-center text-purple-200 hover:text-gold-300 hover:bg-white/10 transition-all duration-200"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  onClick={() => setMobileOpen(false)}
                  className="px-3 py-2.5 rounded-lg text-sm text-center bg-gradient-to-r from-gold-500 to-gold-600 text-indigo-950 font-semibold hover:from-gold-400 hover:to-gold-500 shadow-md shadow-gold-500/20 hover:shadow-gold-500/40 transition-all duration-200"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}