"""Shared fixtures and configuration for tests."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

# Ensure required env vars are set for tests
os.environ.setdefault("EURI_API_KEY", "test-key")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-jwt-secret")


@pytest.fixture
async def test_client():
    """Async test client for FastAPI endpoints."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
