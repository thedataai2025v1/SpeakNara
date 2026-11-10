"""Supabase client singleton."""

from __future__ import annotations

from supabase import Client, create_client

from backend.core.settings import settings


def get_client() -> Client:
    """Return a Supabase client instance."""
    return create_client(
        settings.supabase_url,
        settings.supabase_service_key,
    )


# Lazy singleton
_client: Client | None = None


def get_supabase() -> Client:
    """Get or create the Supabase client singleton."""
    global _client
    if _client is None:
        _client = get_client()
    return _client
