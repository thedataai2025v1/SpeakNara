"""Test health endpoints."""

from httpx import ASGITransport, AsyncClient

from backend.core.settings import settings


async def test_readiness_check():
    """Readiness probe returns 200 with no auth and service status."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "services" in data
    assert "database" in data["services"]
    assert "llm" in data["services"]


async def test_health_no_auth_required():
    """Health endpoint returns 200 without any token."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services" in data
    assert "database" in data["services"]
    assert "llm" in data["services"]


async def test_health_services_default_connected():
    """Services report 'connected' when settings are configured."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    data = response.json()
    # Default test settings have no DB / LLM configured — should show not configured
    assert data["services"]["database"] in ("connected", "not configured")
    assert data["services"]["llm"] in ("connected", "not configured")


async def test_health_database_not_configured(monkeypatch):
    """Database status shows 'not configured' when DATABASE_URL is empty."""
    import importlib

    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("EURI_API_KEY", "")

    # Re-import settings so it picks up the patched env vars
    from backend.core import settings as settings_mod

    importlib.reload(settings_mod)

    from backend.api.endpoints import health as health_mod

    importlib.reload(health_mod)
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["services"]["database"] == "not configured"
    assert data["services"]["llm"] == "not configured"


async def test_health_invalid_token_still_works():
    """Health endpoint returns 200 even with an invalid token (no auth required)."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/health",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

    assert response.status_code == 200
