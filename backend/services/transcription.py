"""Whisper transcription service.

Uses faster-whisper for local audio transcription.
Supports multiple audio formats via pydub conversion.
"""

from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment as WhisperSegment
from pydub import AudioSegment

logger = logging.getLogger(__name__)

# Supported audio formats for transcription
SUPPORTED_FORMATS = {
    ".wav": "wav",
    ".mp3": "mp3",
    ".webm": "webm",
    ".opus": "opus",
    ".m4a": "m4a",
    ".flac": "flac",
}


class TranscriptionError(Exception):
    """Raised when transcription fails."""


@dataclass
class TranscriptionResult:
    """Result of audio transcription."""

    text: str
    language: str
    duration: float
    segments: list[dict[str, Any]] = field(default_factory=list)


async def transcribe_audio(
    file_path: str,
    model: WhisperModel,
    language: str | None = "en",
    with_timestamps: bool = False,
) -> dict[str, Any]:
    """Transcribe an audio file using Whisper.

    Args:
        file_path: Path to the audio file.
        model: Loaded WhisperModel instance.
        language: Language code (e.g., 'en'). None for auto-detection.
        with_timestamps: Include segment-level timestamps in result.

    Returns:
        Dict with 'text', 'language', 'duration', and optionally 'segments'.

    Raises:
        TranscriptionError: If the file is empty, unsupported, or transcription fails.
    """
    # Validate file exists
    if not os.path.exists(file_path):
        raise TranscriptionError(f"File not found: {file_path}")

    # Validate file is not empty
    if os.path.getsize(file_path) == 0:
        raise TranscriptionError("Audio file is empty")

    # Validate file format
    ext = Path(file_path).suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        raise TranscriptionError(f"Unsupported audio format: {ext}. Supported: {list(SUPPORTED_FORMATS.keys())}")

    # Convert to WAV if needed (faster-whisper works best with WAV)
    wav_path = file_path
    if ext != ".wav":
        wav_path = await convert_to_wav(file_path)

    try:
        # Transcribe
        segments_list, info = model.transcribe(
            wav_path,
            language=language,
            beam_size=5,
            vad_filter=True,
        )

        # Build segments
        segment_dicts = []
        for seg in segments_list:
            segment_dicts.append({
                "text": seg.text.strip(),
                "start": seg.start,
                "end": seg.end,
                "avg_logprob": seg.avg_logprob,
            })

        # Determine language
        detected_lang = info.language if info.language else (language or "en")

        # Build result
        full_text = " ".join(seg.text.strip() for seg in segments_list)
        duration = segments_list[-1].end if segments_list else 0.0

        result: dict[str, Any] = {
            "text": full_text,
            "language": detected_lang,
            "duration": duration,
        }

        if with_timestamps:
            result["segments"] = segment_dicts

        logger.info(
            "Transcribed %s: %d segments, %d chars, language=%s",
            file_path,
            len(segment_dicts),
            len(full_text),
            detected_lang,
        )

        return result

    except RuntimeError as e:
        raise TranscriptionError(f"Transcription failed: {e}") from e
    except Exception as e:
        raise TranscriptionError(f"Unexpected error during transcription: {e}") from e


async def convert_to_wav(file_path: str) -> str:
    """Convert an audio file to WAV format for Whisper.

    Args:
        file_path: Path to the source audio file.

    Returns:
        Path to the converted WAV file.
    """
    clip = AudioSegment.from_file(file_path)
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    os.close(tmp_fd)
    clip.export(tmp_path, format="wav")
    return tmp_path


class TranscriptionService:
    """Service class for managing Whisper transcription with lifecycle."""

    def __init__(
        self,
        model_size: str = "medium",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        """Initialize the transcription service.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large).
            device: Device to run on (cpu, cuda).
            compute_type: Compute precision (int8, float16).
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model: WhisperModel | None = None
        self._tmp_files: list[str] = []

    async def initialize(self) -> None:
        """Load the Whisper model."""
        logger.info("Loading Whisper model: %s (%s, %s)", self.model_size, self.device, self.compute_type)
        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
        )
        logger.info("Whisper model loaded successfully")

    async def transcribe(
        self,
        file_path: str,
        language: str | None = "en",
        with_timestamps: bool = False,
    ) -> dict[str, Any]:
        """Transcribe an audio file.

        Args:
            file_path: Path to the audio file.
            language: Language code. None for auto-detection.
            with_timestamps: Include segment-level timestamps.

        Returns:
            Transcription result dict.

        Raises:
            TranscriptionError: If model is not loaded or transcription fails.
        """
        if not self.model:
            raise TranscriptionError("Model not loaded. Call initialize() first.")

        # Convert non-WAV files
        ext = Path(file_path).suffix.lower()
        if ext != ".wav":
            wav_path = await convert_to_wav(file_path)
            self._tmp_files.append(wav_path)
            file_path = wav_path

        return await transcribe_audio(
            file_path=file_path,
            model=self.model,
            language=language,
            with_timestamps=with_timestamps,
        )

    async def cleanup(self) -> None:
        """Clean up temporary files and release model resources."""
        for tmp_file in self._tmp_files:
            try:
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
                    logger.debug("Removed temp file: %s", tmp_file)
            except OSError as e:
                logger.warning("Failed to remove temp file %s: %s", tmp_file, e)
        self._tmp_files.clear()
        self.model = None
        logger.info("Transcription service cleaned up")

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
