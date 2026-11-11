"""Test storytelling endpoint."""

from httpx import ASGITransport, AsyncClient


async def test_generate_returns_valid_structure():
    """Generate returns prompt, story_words, and time_limit fields."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/storytelling/generate")

    assert response.status_code == 200
    data = response.json()
    assert "prompt" in data
    assert "story_words" in data
    assert "time_limit" in data


async def test_generate_prompt_is_non_empty_string():
    """Prompt should be a non-empty string."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/storytelling/generate")

    data = response.json()
    assert isinstance(data["prompt"], str)
    assert len(data["prompt"]) > 0


async def test_generate_story_words_are_strings():
    """Story words should be a list of strings."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/storytelling/generate")

    data = response.json()
    assert isinstance(data["story_words"], list)
    assert len(data["story_words"]) >= 1
    for word in data["story_words"]:
        assert isinstance(word, str)
        assert len(word) > 0


async def test_generate_time_limit_is_reasonable():
    """Time limit should be 60-300 seconds."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/storytelling/generate")

    data = response.json()
    assert isinstance(data["time_limit"], int)
    assert 60 <= data["time_limit"] <= 300
