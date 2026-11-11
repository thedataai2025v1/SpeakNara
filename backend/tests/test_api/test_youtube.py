"""Tests for the YouTube evaluation endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_evaluate_valid_url(client):
    """POST /api/v1/youtube/evaluate returns transcript for valid URL."""
    with patch("backend.api.endpoints.youtube.fetch_youtube_transcript", new_callable=AsyncMock) as mock:
        mock.return_value = {"transcript": "Hello world this is a test", "video_id": "abc123", "word_count": 5}
        response = await client.post("/api/v1/youtube/evaluate", json={"url": "https://youtube.com/watch?v=abc123"})
    assert response.status_code == 200
    data = response.json()
    assert "transcript" in data
    assert data["video_id"] == "abc123"
    assert data["word_count"] == 5


@pytest.mark.asyncio
async def test_evaluate_missing_url(client):
    """Missing URL should return 400."""
    response = await client.post("/api/v1/youtube/evaluate", json={})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_evaluate_transcription_failure(client):
    """Failed transcription should return 500."""
    with patch("backend.api.endpoints.youtube.fetch_youtube_transcript", new_callable=AsyncMock) as mock:
        mock.side_effect = RuntimeError("No transcript found")
        response = await client.post("/api/v1/youtube/evaluate", json={"url": "https://youtube.com/watch?v=abc123"})
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_evaluate_invalid_url_format(client):
    """Invalid URL format should return 400."""
    with patch("backend.api.endpoints.youtube.fetch_youtube_transcript", new_callable=AsyncMock) as mock:
        mock.side_effect = ValueError("Invalid YouTube URL")
        response = await client.post("/api/v1/youtube/evaluate", json={"url": "not-a-url"})
    assert response.status_code == 400
