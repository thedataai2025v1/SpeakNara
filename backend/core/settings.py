"""Environment configuration."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
_env_file = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file)

# ── Application ──────────────────────────────────────────────
APP_NAME: str = os.getenv("APP_NAME", "SpeakNara")
APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# ── Euron API (OpenAI-compatible) ────────────────────────────
EURI_API_KEY: str = os.getenv("EURI_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-5-5")
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.euron.one/api/v1/euri")

# ── Supabase ─────────────────────────────────────────────────
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")

# ── Frontend (CORS) ──────────────────────────────────────────
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
CORS_ORIGINS: list[str] = [
    FRONTEND_URL,
    # Render will set the production URL via env
]
if production_frontend := os.getenv("PRODUCTION_FRONTEND_URL"):
    CORS_ORIGINS.append(production_frontend)
