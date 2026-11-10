"""Test health endpoints."""

from httpx import ASGITransport, AsyncClient

from backend.core.auth import _make_token


async def test_readiness_check():
    """Readiness probe returns 200 with no auth."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


async def test_health_unauthenticated():
    """Health endpoint returns 401 without token."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 401


async def test_health_authenticated():
    """Health endpoint returns 200 with valid token."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = _make_token({"sub": "550e8400-e29b-41b4-941e-001a00000001"})
        response = await client.get(
            "/api/v1/health",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "database" in data


async def test_health_invalid_token():
    """Health endpoint returns 401 with invalid token."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/health",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

    assert response.status_code == 401
