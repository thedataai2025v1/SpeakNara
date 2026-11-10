"""Tests for audio metrics extraction service.

Calculates metrics from transcription results: word count, duration, WPM,
pause detection, and sentence analysis.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock faster_whisper and pydub (used by transcription service)
sys.modules["faster_whisper"] = MagicMock()
sys.modules["faster_whisper.transcribe"] = MagicMock()
sys.modules["pydub"] = MagicMock()
sys.modules["pydub.audio_segment"] = MagicMock()


@pytest.fixture
def mock_segments():
    """Mock transcription segments with text, start/end times."""
    seg1 = MagicMock()
    seg1.text = "Hello world"
    seg1.start = 0.0
    seg1.end = 1.5

    seg2 = MagicMock()
    seg2.text = "This is a test"
    seg2.start = 1.5
    seg2.end = 3.0

    seg3 = MagicMock()
    seg3.text = "SpeakNara is great"
    seg3.start = 5.0
    seg3.end = 7.0

    return [seg1, seg2, seg3]


# --- Word count ---


def test_word_count_basic(mock_segments):
    """Count words from transcription segments."""
    from services.metrics import calculate_word_count

    count = calculate_word_count(mock_segments)
    assert count == 9  # Hello world This is a test SpeakNara is great


def test_word_count_empty():
    """Zero words for empty segments."""
    from services.metrics import calculate_word_count

    count = calculate_word_count([])
    assert count == 0


def test_word_count_single_segment():
    """Count words from a single segment."""
    from services.metrics import calculate_word_count

    seg = MagicMock()
    seg.text = "one two three"

    count = calculate_word_count([seg])
    assert count == 3


# --- Duration ---


def test_duration_basic(mock_segments):
    """Calculate total audio duration from segments."""
    from services.metrics import calculate_duration

    duration = calculate_duration(mock_segments)
    assert duration == 7.0  # last segment ends at 7.0


def test_duration_empty():
    """Zero duration for empty segments."""
    from services.metrics import calculate_duration

    duration = calculate_duration([])
    assert duration == 0.0


# --- WPM (Words Per Minute) ---


def test_wpm_calculation(mock_segments):
    """Calculate words per minute from word count and duration."""
    from services.metrics import calculate_wpm

    # 7 words / 7 seconds = 7/7*60 = 60 WPM
    wpm = calculate_wpm(word_count=7, duration=7.0)
    assert wpm == 60.0


def test_wpm_zero_duration():
    """WPM is 0 when duration is 0."""
    from services.metrics import calculate_wpm

    wpm = calculate_wpm(word_count=10, duration=0.0)
    assert wpm == 0.0


def test_wpm_short_speech():
    """WPM is calculated correctly for short speeches."""
    from services.metrics import calculate_wpm

    # 10 words in 5 seconds = 10/5*60 = 120 WPM
    wpm = calculate_wpm(word_count=10, duration=5.0)
    assert wpm == 120.0


# --- Pause detection ---


def test_pause_detection(mock_segments):
    """Detect pauses between segments."""
    from services.metrics import detect_pauses

    pauses = detect_pauses(mock_segments)
    # seg1 ends at 1.5, seg2 starts at 1.5 -> no pause
    # seg2 ends at 3.0, seg3 starts at 5.0 -> 2.0s pause
    assert len(pauses) == 1
    assert pauses[0]["start"] == 3.0
    assert pauses[0]["end"] == 5.0
    assert pauses[0]["duration"] == 2.0


def test_pause_detection_no_pauses():
    """No pauses when segments are contiguous."""
    seg1 = MagicMock()
    seg1.end = 1.0
    seg2 = MagicMock()
    seg2.start = 1.0

    from services.metrics import detect_pauses

    pauses = detect_pauses([seg1, seg2])
    assert len(pauses) == 0


def test_pause_detection_consecutive_long_pauses():
    """Detect multiple pauses."""
    seg1 = MagicMock()
    seg1.end = 2.0
    seg2 = MagicMock()
    seg2.start = 4.0
    seg2.end = 5.0
    seg3 = MagicMock()
    seg3.start = 10.0

    from services.metrics import detect_pauses

    pauses = detect_pauses([seg1, seg2, seg3])
    assert len(pauses) == 2
    assert pauses[0]["duration"] == 2.0
    assert pauses[1]["duration"] == 5.0


def test_pause_detection_empty():
    """No pauses for empty segments."""
    from services.metrics import detect_pauses

    pauses = detect_pauses([])
    assert len(pauses) == 0


# --- Sentence count ---


def test_sentence_count(mock_segments):
    """Count sentences across all segments."""
    from services.metrics import calculate_sentence_count

    count = calculate_sentence_count(mock_segments)
    assert count == 3


def test_sentence_count_empty():
    """Zero sentences for empty segments."""
    from services.metrics import calculate_sentence_count

    count = calculate_sentence_count([])
    assert count == 0


def test_sentence_count_with_punctuation():
    """Count sentences split by punctuation."""
    seg = MagicMock()
    seg.text = "First sentence. Second sentence! Third?"

    from services.metrics import calculate_sentence_count

    count = calculate_sentence_count([seg])
    assert count >= 3


# --- Full metrics extraction ---


async def test_extract_all_metrics(mock_segments):
    """Extract all metrics in a single call."""
    from services.metrics import extract_all_metrics

    result = await extract_all_metrics(mock_segments)

    assert result["word_count"] == 9
    assert result["duration"] == 7.0
    assert result["wpm"] == pytest.approx(77.142857, abs=0.01)
    assert result["sentence_count"] == 3
    assert result["pause_count"] == 1
    assert len(result["pauses"]) == 1


async def test_extract_all_metrics_empty():
    """Handle empty segments gracefully."""
    from services.metrics import extract_all_metrics

    result = await extract_all_metrics([])

    assert result["word_count"] == 0
    assert result["duration"] == 0.0
    assert result["wpm"] == 0.0
    assert result["sentence_count"] == 0
    assert result["pause_count"] == 0
    assert result["pauses"] == []


# --- Metrics classification ---


def test_wpm_classification_normal():
    """Classify normal WPM (100-150)."""
    from services.metrics import classify_wpm

    category = classify_wpm(125)
    assert category == "normal"


def test_wpm_classification_slow():
    """Classify slow WPM (below 100)."""
    from services.metrics import classify_wpm

    category = classify_wpm(80)
    assert category == "slow"


def test_wpm_classification_fast():
    """Classify fast WPM (above 150)."""
    from services.metrics import classify_wpm

    category = classify_wpm(170)
    assert category == "fast"


def test_wpm_classification_zero():
    """Classify zero WPM as slow."""
    from services.metrics import classify_wpm

    category = classify_wpm(0)
    assert category == "slow"


# --- Edge cases ---


def test_word_count_whitespace_only():
    """Handle segments with only whitespace."""
    seg = MagicMock()
    seg.text = "   "

    from services.metrics import calculate_word_count

    count = calculate_word_count([seg])
    assert count == 0


def test_pause_detection_single_segment():
    """No pauses for a single segment."""
    seg = MagicMock()
    seg.end = 5.0

    from services.metrics import detect_pauses

    pauses = detect_pauses([seg])
    assert len(pauses) == 0


def test_duration_single_segment():
    """Duration is the end time of the last segment."""
    seg = MagicMock()
    seg.end = 12.5

    from services.metrics import calculate_duration

    duration = calculate_duration([seg])
    assert duration == 12.5
