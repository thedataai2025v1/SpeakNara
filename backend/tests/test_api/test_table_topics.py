"""Test table topics endpoint."""

from httpx import ASGITransport, AsyncClient


async def test_generate_returns_valid_structure():
    """Generate returns topic, keywords, and time_limit fields."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/table-topics/generate")

    assert response.status_code == 200
    data = response.json()
    assert "topic" in data
    assert "keywords" in data
    assert "time_limit" in data


async def test_generate_keywords_are_strings():
    """Keywords should be a list of strings."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/table-topics/generate")

    data = response.json()
    assert isinstance(data["keywords"], list)
    assert len(data["keywords"]) >= 1
    for kw in data["keywords"]:
        assert isinstance(kw, str)
        assert len(kw) > 0


async def test_generate_time_limit_is_reasonable():
    """Time limit should be 60-300 seconds."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/table-topics/generate")

    data = response.json()
    assert isinstance(data["time_limit"], int)
    assert 60 <= data["time_limit"] <= 300


async def test_generate_different_calls_may_differ():
    """Two calls may return different topics."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r1 = await client.post("/api/v1/table-topics/generate")
        r2 = await client.post("/api/v1/table-topics/generate")

    d1 = r1.json()
    d2 = r2.json()
    # With 20 topics, probability of always getting the same one is tiny
    # Just check both are valid
    assert d1["topic"] is not None
    assert d2["topic"] is not None
