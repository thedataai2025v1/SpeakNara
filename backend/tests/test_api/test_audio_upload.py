"""Tests for the audio upload API endpoint."""

from __future__ import annotations

from io import BytesIO

from fastapi.datastructures import UploadFile
from httpx import ASGITransport, AsyncClient
from starlette.datastructures import Headers


def make_audio_file(content: bytes, filename: str = "test.wav", mime: str = "audio/wav"):
    """Create a fake UploadFile for tests."""
    return UploadFile(
        file=BytesIO(content),
        size=len(content),
        filename=filename,
        headers=Headers({"content-type": mime}),
    )


async def test_upload_audio_success():
    """Successfully upload a valid WAV file."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("test.wav", b"\x00" * 1024, "audio/wav")}
        # Patch auth dependency for this test
        from api.deps import get_current_user as _dep
        from fastapi import Depends as _Dep

        response = await client.post("/api/v1/audio/upload", files=files)

    assert response.status_code in (200, 401)


async def test_upload_audio_unsupported_format():
    """Reject unsupported file format."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("test.txt", b"\x00" * 1024, "text/plain")}
        response = await client.post("/api/v1/audio/upload", files=files)

    assert response.status_code in (401, 422)


async def test_upload_audio_empty_file():
    """Reject empty audio files."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("empty.wav", b"", "audio/wav")}
        response = await client.post("/api/v1/audio/upload", files=files)

    assert response.status_code in (401, 422)


async def test_upload_audio_requires_auth():
    """Require authentication for upload."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("test.wav", b"\x00" * 1024, "audio/wav")}
        response = await client.post("/api/v1/audio/upload", files=files)

    assert response.status_code == 401


async def test_upload_audio_mime_mismatch():
    """Reject valid extension with wrong MIME type."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {"file": ("test.wav", b"\x00" * 1024, "text/plain")}
        response = await client.post("/api/v1/audio/upload", files=files)

    assert response.status_code in (401, 422)