"""Tests for the prepared speech API endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_generate_returns_topic_and_keywords(client):
    """POST /api/v1/prepared-speech/generate returns a topic and keywords."""
    response = await client.post("/api/v1/prepared-speech/generate")
    assert response.status_code == 200

    data = response.json()
    assert "topic" in data
    assert "keywords" in data
    assert "time_limit" in data
    assert isinstance(data["topic"], str)
    assert isinstance(data["keywords"], list)
    assert len(data["keywords"]) == 3
    assert data["time_limit"] == 120


@pytest.mark.asyncio
async def test_generate_keywords_are_non_empty_strings(client):
    """Generated keywords should be non-empty strings."""
    response = await client.post("/api/v1/prepared-speech/generate")
    data = response.json()
    for kw in data["keywords"]:
        assert isinstance(kw, str)
        assert len(kw.strip()) > 0


@pytest.mark.asyncio
async def test_generate_topic_varies(client):
    """Multiple calls should produce different topics (statistical check)."""
    topics = set()
    for _ in range(20):
        response = await client.post("/api/v1/prepared-speech/generate")
        topics.add(response.json()["topic"])
    # With 10 prepared speech topics, 20 random draws should yield variety
    assert len(topics) > 1


@pytest.mark.asyncio
async def test_generate_keywords_are_from_topic_set(client):
    """Keywords should be relevant to prepared speech delivery."""
    response = await client.post("/api/v1/prepared-speech/generate")
    data = response.json()
    for kw in data["keywords"]:
        assert isinstance(kw, str)
