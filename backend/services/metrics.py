"""Audio metrics extraction service.

Calculates metrics from Whisper transcription results:
- Word count
- Duration
- Words per minute (WPM)
- Pause detection
- Sentence count
- WPM classification
"""

from __future__ import annotations

import re


def calculate_word_count(segments) -> int:
    """Count total words across all transcription segments."""
    total = 0
    for segment in segments:
        text = segment.text.strip()
        if text:
            total += len(text.split())
    return total


def calculate_duration(segments) -> float:
    """Calculate total audio duration from the last segment's end time."""
    if not segments:
        return 0.0
    return segments[-1].end


def calculate_wpm(word_count: int, duration: float) -> float:
    """Calculate words per minute. Returns 0.0 if duration is 0."""
    if duration <= 0:
        return 0.0
    return (word_count / duration) * 60


def detect_pauses(segments, min_pause_duration: float = 0.5) -> list[dict]:
    """Detect pauses between consecutive segments.

    A pause is a gap between one segment's end and the next segment's start
    that exceeds min_pause_duration seconds.

    Returns a list of dicts with keys: start, end, duration.
    """
    pauses = []
    for i in range(len(segments) - 1):
        gap_start = segments[i].end
        gap_end = segments[i + 1].start
        gap_duration = gap_end - gap_start
        if gap_duration >= min_pause_duration:
            pauses.append({
                "start": gap_start,
                "end": gap_end,
                "duration": gap_duration,
            })
    return pauses


def calculate_sentence_count(segments) -> int:
    """Count sentences across all segments.

    Sentences are split by common sentence-ending punctuation (. ! ?).
    Each non-empty segment with no sentence-ending punctuation counts as one sentence.
    """
    total = 0
    sentence_pattern = re.compile(r"[.!?]")
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        sentences = sentence_pattern.split(text)
        # Filter empty strings
        sentences = [s for s in sentences if s.strip()]
        if sentences:
            total += len(sentences)
        else:
            # No sentence-ending punctuation: count as one sentence
            total += 1
    return total


def classify_wpm(wpm: float) -> str:
    """Classify WPM into a category.

    - slow: below 100
    - normal: 100-150
    - fast: above 150
    """
    if wpm < 100:
        return "slow"
    elif wpm <= 150:
        return "normal"
    else:
        return "fast"


async def extract_all_metrics(segments) -> dict:
    """Extract all audio metrics from transcription segments.

    Returns a dict with all calculated metrics.
    """
    word_count = calculate_word_count(segments)
    duration = calculate_duration(segments)
    wpm = calculate_wpm(word_count, duration)
    sentence_count = calculate_sentence_count(segments)
    pauses = detect_pauses(segments)

    return {
        "word_count": word_count,
        "duration": duration,
        "wpm": wpm,
        "sentence_count": sentence_count,
        "pause_count": len(pauses),
        "pauses": pauses,
    }
