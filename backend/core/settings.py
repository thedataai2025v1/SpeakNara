"""Environment configuration via pydantic-settings."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# ── Application ──────────────────────────────────────────────


class Settings(BaseSettings):
    """All config loaded from env / .env with typed defaults."""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────
    app_name: str = "SpeakNara"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── Euron API (OpenAI-compatible) ──────────────────────
    euri_api_key: str = ""
    llm_model: str = "claude-sonnet-5-5"
    llm_base_url: str = "https://api.euron.one/api/v1/euri"

    # ── Supabase ───────────────────────────────────────────
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_jwt_secret: str = ""

    # ── Frontend (CORS) ────────────────────────────────────
    frontend_url: str = "http://localhost:3000"
    production_frontend_url: str = ""

    @property
    def cors_origins(self) -> list[str]:
        origins = [self.frontend_url]
        if self.production_frontend_url:
            origins.append(self.production_frontend_url)
        return origins


# Singleton instance
settings = Settings()
