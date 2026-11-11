"""YouTube transcript service — extract transcript from YouTube videos."""

import logging
import os
import time

import httpx

logger = logging.getLogger(__name__)


def _extract_video_id(url: str) -> str:
    """Extract the YouTube video ID from various URL formats."""
    for prefix in ("https://www.youtube.com/watch?v=", "https://youtube.com/watch?v=",
                   "https://youtu.be/", "https://www.youtu.be/"):
        if prefix in url:
            video_id = url.split(prefix)[-1].split("&")[0].split("?")[0]
            return video_id
    if url.startswith("http"):
        raise ValueError(f"Could not extract video ID from URL: {url}")
    if len(url) == 11:
        return url
    raise ValueError(f"Could not extract video ID from: {url}")


async def fetch_youtube_transcript(url: str, language: str = "en") -> dict:
    """Fetch YouTube video transcript using YouTube Transcript API library.

    Returns dict with transcript text and metadata.
    Falls back to Whisper transcription via YouTube_DL if the library transcript fails.
    """
    video_id = _extract_video_id(url)
    logger.info("Fetching transcript for YouTube video %s", video_id)

    # Try to use youtube-transcript-api library first
    transcript_text = _try_library_transcript(video_id, language)

    if not transcript_text:
        logger.info("Library transcript unavailable for %s, using Whisper fallback", video_id)
        transcript_text = _whisper_fallback(video_id)

    word_count = len(transcript_text.split())

    return {
        "video_id": video_id,
        "url": url,
        "transcript": transcript_text,
        "word_count": word_count,
        "method": "library" if transcript_text != _whisper_fallback(video_id) else "whisper",
    }


def _try_library_transcript(video_id: str, language: str) -> str:
    """Try to fetch transcript using youtube-transcript-api library."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabledError, VideoUnavailableError  # noqa: F401

        youtube_api = YouTubeTranscriptApi()
        transcripts = youtube_api.list(video_id)

        # Try exact language match first
        for t in transcripts:
            if t.language_code == language:
                raw = youtube_api.fetch(transcripts=[t], video_id=video_id)
                return " ".join(entry["text"] for entry in raw)

        # Fall back to any available transcript
        if transcripts:
            raw = youtube_api.fetch(transcripts=[transcripts[0]], video_id=video_id)
            return " ".join(entry["text"] for entry in raw)

    except ImportError:
        logger.info("youtube-transcript-api not installed, will use Whisper fallback")
    except Exception as exc:
        logger.info("Library transcript failed for %s: %s", video_id, exc)

    return ""


def _whisper_fallback(video_id: str) -> str:
    """Download audio from YouTube and transcribe with Whisper.

    This uses yt-dlp to download the audio, then Whisper to transcribe it.
    """
    import tempfile

    from faster_whisper import WhisperModel
    import subprocess

    model_size = os.getenv("WHISPER_MODEL", "medium")

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        subprocess.run(
            [
                "yt-dlp", "-x", "--audio-format", "wav",
                "-o", tmp_path.replace(".webm", ".wav"),
                f"https://www.youtube.com/watch?v={video_id}",
            ],
            check=True,
            capture_output=True,
            timeout=300,
        )
        wav_path = tmp_path.replace(".webm", ".wav")

        logger.info("Loading Whisper model %s for YouTube transcription", model_size)
        whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = whisper_model.transcribe(wav_path, beam_size=5)
        segments_list = list(segments)

        transcript = " ".join(seg.text for seg in segments_list)
        logger.info("Whisper transcribed YouTube video %s: %d words", video_id, len(transcript.split()))
        return transcript.strip()

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        logger.error("yt-dlp failed for %s: %s", video_id, exc)
        raise RuntimeError(f"Failed to download audio from YouTube: {exc}") from exc
    finally:
        for ext in (".webm", ".wav"):
            p = tmp_path.replace(".webm", ext)
            if os.path.exists(p):
                os.remove(p)
