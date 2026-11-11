"""Analysis orchestrator — ties transcription, metrics, LLM feedback and DB storage.

The orchestrator coordinates:
  1. Compute speech metrics (word count, speaking rate, etc.) from the transcript.
  2. Generate LLM feedback (overall_score, strengths, improvements, tips).
  3. Persist session + metrics + feedback into the local SQLite database.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any

from core.database import get_connection
from services.llm_service import get_llm_feedback, LLMError
from services.metrics import (
    calculate_wpm,
)


@dataclass
class AnalysisResult:
    """Returned by run_analysis; contains every piece of data the frontend needs."""

    session_id: str
    user_id: str
    mode: str
    metrics: dict[str, Any]
    feedback: dict[str, Any]
    audio_url: str | None = None
    topic: str | None = None
    story_words: list[str] | None = None
    role: str | None = None


class OrchestrationError(Exception):
    """Wrapped error from any stage of the pipeline."""


# ------------------------------------------------------------------ #
#  Helpers — compute metrics from text (no Whisper segments needed)  #
# ------------------------------------------------------------------ #


def _compute_metrics(transcript: str, duration: float, role: str | None) -> dict[str, Any]:
    """Compute speech metrics from a plain transcript and duration.

    Mirrors what `extract_all_metrics` does when starting from Whisper
    segments, but works directly with text.
    """
    import re

    words = transcript.split()
    word_count = len(words)
    unique_ratio = len(set(w.lower() for w in words)) / word_count if words else 0.0

    sentences = [s.strip() for s in re.split(r"[.!?]+", transcript.strip()) if s.strip()]
    sentence_count = len(sentences)

    if duration > 0:
        est_duration = duration
    elif word_count > 0:
        est_duration = word_count / 150.0 * 60.0  # estimate at ~150 WPM
    else:
        est_duration = 0.0

    rate = calculate_wpm(word_count, est_duration) if est_duration > 0 else 0.0

    avg_sentence_len = word_count / sentence_count if sentence_count > 0 else 0.0

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "speaking_rate": round(rate, 1),
        "avg_sentence_length": round(avg_sentence_len, 1),
        "pause_count": 0,
        "unique_word_ratio": round(unique_ratio, 2),
        "filler_word_count": 0,
        "estimated_duration": round(est_duration, 1),
        "role": role or "member",
    }


def _metrics_summary(metrics: dict[str, Any]) -> str:
    """Build a one-line metrics summary string for the LLM prompt."""
    return (
        f"Words: {metrics['word_count']} | "
        f"Sentences: {metrics['sentence_count']} | "
        f"Rate: {metrics['speaking_rate']} wpm | "
        f"Avg sentence length: {metrics['avg_sentence_length']} | "
        f"Unique word ratio: {metrics['unique_word_ratio']} | "
        f"Filler words: {metrics['filler_word_count']}"
    )


# ------------------------------------------------------------------ #
#  Storage helpers                                                    #
# ------------------------------------------------------------------ #


def _store_session(conn, session_id: str, user_id: str, mode: str, transcript: str, audio_url: str | None, topic: str | None) -> None:
    """Insert session row (idempotent on first insert)."""
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO sessions (id, user_id, mode, transcript, audio_url, created_at)
           VALUES (?, ?, ?, ?, ?, datetime('now'))""",
        (session_id, user_id, mode, transcript, audio_url),
    )


def _store_metrics(conn, session_id: str, metrics: dict[str, Any]) -> None:
    """Insert metrics row linked to the session."""
    cur = conn.cursor()
    metrics_id = str(uuid.uuid4())
    cur.execute(
        """INSERT INTO metrics (id, session_id, word_count, speaking_rate,
                               avg_sentence_length, pause_count, unique_word_ratio,
                               filler_word_count, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
        (
            metrics_id,
            session_id,
            metrics.get("word_count", 0),
            metrics.get("speaking_rate", 0.0),
            metrics.get("avg_sentence_length", 0.0),
            metrics.get("pause_count", 0),
            metrics.get("unique_word_ratio", 0.0),
            metrics.get("filler_word_count", 0),
        ),
    )


def _store_feedback(conn, session_id: str, feedback: dict[str, Any]) -> None:
    """Insert feedback row linked to the session."""
    cur = conn.cursor()
    feedback_id = str(uuid.uuid4())

    # Normalise list fields to JSON strings for storage
    strengths = feedback.get("strengths", [])
    improvements = feedback.get("improvements", [])
    tips = feedback.get("tips", [])

    cur.execute(
        """INSERT INTO feedback (id, session_id, overall_score, strengths,
                                improvements, tips, created_at)
           VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
        (
            feedback_id,
            session_id,
            feedback.get("overall_score", 0),
            json.dumps(strengths),
            json.dumps(improvements),
            json.dumps(tips),
        ),
    )


# ------------------------------------------------------------------ #
#  Main entry point                                                   #
# ------------------------------------------------------------------ #


def run_analysis(
    user_id: str,
    transcript: str,
    mode: str,
    *,
    audio_url: str | None = None,
    topic: str | None = None,
    story_words: list[str] | None = None,
    role: str | None = None,
    duration: float = 0.0,
) -> AnalysisResult:
    """Run the full analysis pipeline.

    1. Compute metrics from the transcript.
    2. Call the LLM for qualitative feedback.
    3. Persist everything to the local SQLite database.

    Raises `OrchestrationError` if any stage fails.
    """
    session_id = str(uuid.uuid4())

    # --- Step 1: metrics ---
    try:
        metrics = _compute_metrics(transcript, duration, role)
    except Exception as exc:
        raise OrchestrationError(f"Metrics computation failed: {exc}") from exc

    # --- Step 2: LLM feedback ---
    try:
        summary = _metrics_summary(metrics)
        feedback = get_llm_feedback(
            transcript=transcript,
            metrics_summary=summary,
            mode=mode,
            topic=topic,
            story_words=story_words,
            role=role,
        )
    except (LLMError, Exception) as exc:
        raise OrchestrationError(f"LLM feedback failed: {exc}") from exc

    # --- Step 3: persist to DB ---
    conn = get_connection()
    try:
        _store_session(conn, session_id, user_id, mode, transcript, audio_url, topic)
        _store_metrics(conn, session_id, metrics)
        _store_feedback(conn, session_id, feedback)
        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise OrchestrationError(f"DB storage failed: {exc}") from exc
    finally:
        conn.close()

    return AnalysisResult(
        session_id=session_id,
        user_id=user_id,
        mode=mode,
        metrics=metrics,
        feedback=feedback,
        audio_url=audio_url,
        topic=topic,
        story_words=story_words,
        role=role,
    )
