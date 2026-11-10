"""Test health endpoint."""
from httpx import ASGITransport, AsyncClient


async def test_health_check():
    """Health endpoint returns 200 with status ok."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
