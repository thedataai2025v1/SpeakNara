"""Tests for audio upload validation service."""

from __future__ import annotations

from io import BytesIO

import pytest

from services.audio_upload import AudioUploadError, validate_audio


@pytest.mark.parametrize(
    "ext,mime,max_size",
    [
        (".wav", "audio/wav", 50 * 1024 * 1024),
        (".mp3", "audio/mpeg", 50 * 1024 * 1024),
        (".webm", "audio/webm", 50 * 1024 * 1024),
        (".opus", "audio/opus", 50 * 1024 * 1024),
    ],
)
def test_validate_audio_accepts_valid_formats(ext: str, mime: str, max_size: int):
    """Accept WAV, MP3, WebM, Opus files under 50 MB."""
    content = b"\x00" * 1024  # dummy 1 KB file
    result = validate_audio(content, f"test{ext}", mime, max_size)
    assert result is None  # no error


@pytest.mark.parametrize(
    "ext,mime",
    [
        (".txt", "text/plain"),
        (".jpg", "image/jpeg"),
        (".pdf", "application/pdf"),
        (".exe", "application/octet-stream"),
    ],
)
def test_validate_audio_rejects_unsupported_formats(ext: str, mime: str):
    """Reject non-audio file extensions."""
    content = b"\x00" * 1024
    with pytest.raises(AudioUploadError, match="Unsupported"):
        validate_audio(content, f"test{ext}", mime, 50 * 1024 * 1024)


def test_validate_audio_rejects_oversized_files():
    """Reject files larger than 50 MB."""
    content = b"\x00" * 1024
    with pytest.raises(AudioUploadError, match="too large|exceeds|max.*size"):
        validate_audio(content, "test.wav", "audio/wav", max_size=1024)  # 1 KB limit


def test_validate_audio_rejects_empty_files():
    """Reject empty audio files."""
    with pytest.raises(AudioUploadError, match="empty|zero|no data"):
        validate_audio(b"", "test.wav", "audio/wav", 50 * 1024 * 1024)


def test_validate_audio_rejects_bad_mime_even_valid_ext():
    """Reject valid extension with wrong MIME type."""
    content = b"\x00" * 1024
    with pytest.raises(AudioUploadError, match="mismatch|wrong.*type|invalid.*mime|mime.*invalid"):
        validate_audio(content, "test.wav", "text/plain", 50 * 1024 * 1024)
