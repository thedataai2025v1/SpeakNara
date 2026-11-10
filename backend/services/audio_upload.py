"""Audio file validation service."""

from __future__ import annotations

# Supported audio formats: (extension, allowed mime types)
SUPPORTED_FORMATS = {
    ".wav": {"audio/wav", "audio/x-wav", "audio/vnd.wave"},
    ".mp3": {"audio/mpeg", "audio/mpeg3", "audio/mp3"},
    ".webm": {"audio/webm", "video/webm"},
    ".opus": {"audio/opus", "audio/OGG", "audio/x-ogg"},
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


class AudioUploadError(Exception):
    """Raised when audio file validation fails."""


def validate_audio(
    content: bytes,
    filename: str,
    mime_type: str,
    max_size: int = MAX_FILE_SIZE,
) -> None | str:
    """Validate an uploaded audio file.

    Args:
        content: Raw file content.
        filename: Original filename (used to extract extension).
        mime_type: MIME type from the upload.
        max_size: Maximum allowed file size in bytes.

    Returns:
        ``None`` on success, ``None`` on validation pass.
    Raises:
        AudioUploadError: If the file is unsupported, too large, or empty.
    """
    if not content:
        raise AudioUploadError("Audio file is empty")

    if len(content) >= max_size:
        mb = len(content) / (1024 * 1024)
        raise AudioUploadError(
            f"Audio file too large: {mb:.1f} MB exceeds maximum allowed size"
        )

    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    allowed_mimes = SUPPORTED_FORMATS.get(ext)

    if not allowed_mimes:
        raise AudioUploadError(
            f"Unsupported file format '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    if mime_type.lower() not in allowed_mimes:
        raise AudioUploadError(
            f"Invalid MIME type mismatch: '{mime_type}' does not match format '{ext}'"
        )

    return None
