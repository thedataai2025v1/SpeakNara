"""Tests for Whisper transcription service.

All tests use mocks — no real whisper model is loaded.
Mock faster_whisper and pydub at the import level before importing the service.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock faster_whisper and pydub before importing the service
sys.modules["faster_whisper"] = MagicMock()
sys.modules["faster_whisper.transcribe"] = MagicMock()
sys.modules["pydub"] = MagicMock()
sys.modules["pydub.audio_segment"] = MagicMock()


@pytest.fixture
def mock_whisper_model():
    """Mock faster-whisper WhisperModel."""
    model = MagicMock()
    model.batch_size = 8
    return model


@pytest.fixture
def mock_whisper_segments():
    """Mock transcription segments from faster-whisper."""
    seg1 = MagicMock()
    seg1.text = " Hello "
    seg1.start = 0.0
    seg1.end = 1.5
    seg1.avg_logprob = -0.5

    seg2 = MagicMock()
    seg2.text = " world "
    seg2.start = 1.5
    seg2.end = 3.0
    seg2.avg_logprob = -0.3

    info = MagicMock()
    info.language = "en"
    info.all_language_probs = []

    return [seg1, seg2], info


# --- Service tests ---


async def test_transcribe_audio(mock_whisper_model, mock_whisper_segments):
    """Transcribe an audio file and return full text."""
    from services.transcription import transcribe_audio

    segments, info = mock_whisper_segments
    mock_whisper_model.transcribe.return_value = (segments, info)

    with patch("os.path.exists", return_value=True):
        with patch("os.path.getsize", return_value=1024):
            result = await transcribe_audio(
                file_path="/tmp/test.wav",
                model=mock_whisper_model,
                language="en",
            )

    assert "Hello" in result["text"]
    assert "world" in result["text"]
    assert result["language"] == "en"
    assert result["duration"] == 3.0


async def test_transcribe_audio_empty_file():
    """Raise an error for empty audio files."""
    from services.transcription import TranscriptionError, transcribe_audio

    mock_model = MagicMock()

    with patch("os.path.exists", return_value=True):
        with patch("os.path.getsize", return_value=0):
            with pytest.raises(TranscriptionError, match="empty"):
                await transcribe_audio(
                    file_path="/tmp/empty.wav",
                    model=mock_model,
                    language="en",
                )


async def test_transcribe_audio_unsupported_format():
    """Reject unsupported audio formats."""
    from services.transcription import TranscriptionError, transcribe_audio

    mock_model = MagicMock()

    with patch("os.path.exists", return_value=True):
        with patch("os.path.getsize", return_value=1024):
            with pytest.raises(TranscriptionError, match="Unsupported"):
                await transcribe_audio(
                    file_path="/tmp/test.txt",
                    model=mock_model,
                    language="en",
                )


async def test_transcribe_audio_language_detection(mock_whisper_model, mock_whisper_segments):
    """Detect language when not specified."""
    from services.transcription import transcribe_audio

    segments, info = mock_whisper_segments
    mock_whisper_model.transcribe.return_value = (segments, info)

    with patch("os.path.exists", return_value=True):
        with patch("os.path.getsize", return_value=1024):
            result = await transcribe_audio(
                file_path="/tmp/test.wav",
                model=mock_whisper_model,
                language=None,
            )

    assert result["language"] is not None


async def test_transcribe_audio_with_timestamps(mock_whisper_model, mock_whisper_segments):
    """Include word-level timestamps when requested."""
    from services.transcription import transcribe_audio

    segments, info = mock_whisper_segments
    mock_whisper_model.transcribe.return_value = (segments, info)

    with patch("os.path.exists", return_value=True):
        with patch("os.path.getsize", return_value=1024):
            result = await transcribe_audio(
                file_path="/tmp/test.wav",
                model=mock_whisper_model,
                language="en",
                with_timestamps=True,
            )

    assert "segments" in result
    assert len(result["segments"]) == 2
    assert result["segments"][0]["start"] == 0.0
    assert result["segments"][0]["end"] == 1.5
    assert "Hello" in result["segments"][0]["text"]


async def test_transcribe_audio_model_error():
    """Handle whisper model errors gracefully."""
    from services.transcription import TranscriptionError, transcribe_audio

    mock_model = MagicMock()
    mock_model.transcribe.side_effect = RuntimeError("GPU out of memory")

    with patch("os.path.exists", return_value=True):
        with patch("os.path.getsize", return_value=1024):
            with pytest.raises(TranscriptionError, match="Transcription failed"):
                await transcribe_audio(
                    file_path="/tmp/test.wav",
                    model=mock_model,
                    language="en",
                )


async def test_transcribe_audio_file_not_found():
    """Raise an error when the file does not exist."""
    from services.transcription import TranscriptionError, transcribe_audio

    mock_model = MagicMock()

    with patch("os.path.exists", return_value=False):
        with pytest.raises(TranscriptionError, match="not found"):
            await transcribe_audio(
                file_path="/tmp/nonexistent.wav",
                model=mock_model,
                language="en",
            )


# --- Format conversion tests ---


async def test_convert_to_wav():
    """Convert audio file to WAV format for whisper."""
    from services.transcription import convert_to_wav

    mock_clip = MagicMock()
    mock_export = MagicMock()
    mock_clip.export.return_value = mock_export

    with patch("services.transcription.AudioSegment") as MockAudio:
        MockAudio.from_file.return_value = mock_clip

        with patch("services.transcription.tempfile.mkstemp", return_value=(99, "/tmp/converted.wav")):
            with patch("os.close"):
                result = await convert_to_wav("/tmp/test.mp3")

    MockAudio.from_file.assert_called_once_with("/tmp/test.mp3")
    mock_clip.export.assert_called()
    assert result == "/tmp/converted.wav"


async def test_convert_already_wav():
    """WAV files still go through pydub for format normalization."""
    from services.transcription import convert_to_wav

    mock_clip = MagicMock()
    mock_clip.export.return_value = MagicMock()

    with patch("services.transcription.AudioSegment") as MockAudio:
        MockAudio.from_file.return_value = mock_clip

        with patch("services.transcription.tempfile.mkstemp", return_value=(99, "/tmp/converted.wav")):
            with patch("os.close"):
                await convert_to_wav("/tmp/test.wav")

    MockAudio.from_file.assert_called_once_with("/tmp/test.wav")


# --- Service class tests ---


async def test_transcription_service_init():
    """Initialize transcription service with model."""
    from services.transcription import TranscriptionService

    service = TranscriptionService(model_size="tiny", device="cpu")
    assert service.model_size == "tiny"
    assert service.device == "cpu"
    assert service.model is None
    assert service._tmp_files == []


async def test_transcription_service_initialize():
    """Load the Whisper model on initialize."""
    from services.transcription import TranscriptionService

    with patch("services.transcription.WhisperModel") as MockWhisper:
        service = TranscriptionService(model_size="tiny", device="cpu")
        await service.initialize()

        MockWhisper.assert_called_once_with("tiny", device="cpu", compute_type="int8")
        assert service.model is not None


async def test_transcription_service_transcribe(mock_whisper_model, mock_whisper_segments):
    """Transcribe using the service class."""
    from services.transcription import TranscriptionService

    segments, info = mock_whisper_segments
    mock_whisper_model.transcribe.return_value = (segments, info)

    service = TranscriptionService()
    service.model = mock_whisper_model

    with patch("os.path.exists", return_value=True):
        with patch("os.path.getsize", return_value=1024):
            result = await service.transcribe("/tmp/test.wav", language="en")

    assert "text" in result
    assert "Hello" in result["text"]


async def test_transcription_service_transcribe_not_initialized():
    """Raise error if model is not loaded."""
    from services.transcription import TranscriptionError, TranscriptionService

    service = TranscriptionService()

    with pytest.raises(TranscriptionError, match="not loaded"):
        await service.transcribe("/tmp/test.wav", language="en")


async def test_transcription_service_cleanup():
    """Clean up temporary files on service shutdown."""
    from services.transcription import TranscriptionService

    mock_model = MagicMock()
    service = TranscriptionService()
    service.model = mock_model
    service._tmp_files = ["/tmp/converted1.wav", "/tmp/converted2.wav"]

    with patch("os.path.exists", return_value=True):
        with patch("os.remove") as mock_remove:
            await service.cleanup()

    assert mock_remove.call_count == 2
    assert service._tmp_files == []
    assert service.model is None


async def test_transcription_service_context_manager():
    """Use service as an async context manager."""
    from services.transcription import TranscriptionService

    with patch("services.transcription.WhisperModel") as MockWhisper:
        with patch("os.remove"):
            async with TranscriptionService(model_size="tiny") as service:
                assert service.model is not None

            # After exiting context, cleanup should have been called
            assert service.model is None