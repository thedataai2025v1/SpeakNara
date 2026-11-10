"""Test settings configuration."""

import os
from unittest.mock import patch

from backend.core.settings import Settings


def test_settings_defaults():
    """Settings falls back to defaults when env vars are absent."""
    env = dict(os.environ)
    # Strip all settings-related vars
    for key in list(env.keys()):
        if key.upper().startswith(
            ("APP_", "EURI_", "LLM_", "SUPABASE_", "FRONTEND_", "PRODUCTION_")
        ):
            del env[key]

    with patch.dict(os.environ, env, clear=True):
        s = Settings(_env_file="")
        assert s.app_name == "SpeakNara"
        assert s.app_version == "0.1.0"
        assert s.debug is False
        assert s.euri_api_key == ""
        assert s.llm_model == "claude-sonnet-5-5"
        assert s.llm_base_url == "https://api.euron.one/api/v1/euri"
        assert s.supabase_url == ""
        assert s.supabase_service_key == ""
        assert s.supabase_jwt_secret == ""
        assert s.frontend_url == "http://localhost:3000"
        assert s.cors_origins == ["http://localhost:3000"]


def test_settings_from_env():
    """Settings reads values from environment variables."""
    extra = {
        "APP_NAME": "TestApp",
        "APP_VERSION": "2.0.0",
        "DEBUG": "true",
        "EURI_API_KEY": "sk-test123",
        "LLM_MODEL": "gpt-4o",
        "SUPABASE_URL": "https://example.supabase.co",
        "SUPABASE_SERVICE_KEY": "sb-key",
        "SUPABASE_JWT_SECRET": "jwt-secret",
        "FRONTEND_URL": "http://localhost:3001",
        "PRODUCTION_FRONTEND_URL": "https://prod.example.com",
    }

    with patch.dict(os.environ, extra, clear=True):
        s = Settings(_env_file="")
        assert s.app_name == "TestApp"
        assert s.app_version == "2.0.0"
        assert s.debug is True
        assert s.euri_api_key == "sk-test123"
        assert s.llm_model == "gpt-4o"
        assert s.supabase_url == "https://example.supabase.co"
        assert s.supabase_service_key == "sb-key"
        assert s.supabase_jwt_secret == "jwt-secret"
        assert "http://localhost:3001" in s.cors_origins
        assert "https://prod.example.com" in s.cors_origins
