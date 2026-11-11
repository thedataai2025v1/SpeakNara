"""Tests for the analysis orchestrator.

The orchestrator coordinates:
  1. Compute speech metrics (word count, speaking rate, etc.) from the transcript.
  2. Generate LLM feedback (overall_score, strengths, improvements, tips).
  3. Persist session + metrics + feedback into the local SQLite database.
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from services.analysis_orchestrator import (
    AnalysisResult,
    OrchestrationError,
    _compute_metrics,
    _metrics_summary,
    run_analysis,
)


# -- Fixtures -- #


@pytest.fixture
def sample_transcript():
    return """Hello everyone. Today I'd like to talk about the importance of
    clean water in our daily lives. Water is essential for survival, health,
    and economic development. Many people around the world still lack access
    to safe drinking water."""


@pytest.fixture
def sample_metrics():
    return {
        "word_count": 40,
        "sentence_count": 4,
        "speaking_rate": 133.3,
        "avg_sentence_length": 10.0,
        "pause_count": 0,
        "unique_word_ratio": 0.85,
        "filler_word_count": 0,
        "estimated_duration": 18.0,
        "role": "member",
    }


@pytest.fixture
def sample_feedback():
    return {
        "overall_score": 7,
        "strengths": ["Clear pronunciation", "Good pacing"],
        "improvements": ["Add more variety in tone", "Use more transitions"],
        "tips": ["Practice breathing exercises", "Record and listen back"],
    }


# -- Tests: _compute_metrics -- #


class TestComputeMetrics:
    def test_basic_metrics(self):
        transcript = "Hello world this is a test of the metrics computation."
        result = _compute_metrics(transcript, 5.0, "member")

        assert result["word_count"] == 10
        assert result["role"] == "member"

    def test_zero_duration_estimates(self):
        transcript = "One two three four five six seven eight nine ten."
        result = _compute_metrics(transcript, 0.0, None)

        assert result["word_count"] == 10
        assert result["estimated_duration"] > 0
        assert result["role"] == "member"

    def test_empty_transcript(self):
        result = _compute_metrics("", 0.0, None)

        assert result["word_count"] == 0
        assert result["speaking_rate"] == 0.0
        assert result["sentence_count"] == 0

    def test_filler_words_zero_for_text_only(self):
        transcript = "Um, uh, so, like, I think that is good."
        result = _compute_metrics(transcript, 3.0, None)

        assert result["filler_word_count"] == 0  # text-only can't count fillers

    def test_custom_role(self):
        transcript = "Hello world."
        result = _compute_metrics(transcript, 1.0, "teacher")

        assert result["role"] == "teacher"

    def test_avg_sentence_length(self):
        transcript = "One sentence here. Second sentence here. Third one."
        result = _compute_metrics(transcript, 3.0, None)

        assert result["avg_sentence_length"] > 0
        assert result["sentence_count"] == 3


# -- Tests: _metrics_summary -- #


class TestMetricsSummary:
    def test_produces_string(self, sample_metrics):
        summary = _metrics_summary(sample_metrics)
        assert isinstance(summary, str)
        assert "Words: 40" in summary
        assert "Rate: 133.3 wpm" in summary

    def test_includes_all_fields(self, sample_metrics):
        summary = _metrics_summary(sample_metrics)
        assert "Sentences:" in summary
        assert "Avg sentence length:" in summary
        assert "Unique word ratio:" in summary
        assert "Filler words:" in summary


# -- Tests: run_analysis (happy path) -- #


class TestRunAnalysisHappyPath:
    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_returns_analysis_result(self, mock_conn, mock_llm, sample_transcript, sample_metrics, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        result = run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="fluency",
            duration=18.0,
        )

        assert isinstance(result, AnalysisResult)
        assert result.user_id == "user-123"
        assert result.mode == "fluency"

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_calls_llm_with_correct_params(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="fluency",
            topic="water",
            story_words=["water", "clean"],
            role="member",
            duration=18.0,
        )

        mock_llm.assert_called_once_with(
            transcript=sample_transcript,
            metrics_summary=mock_llm.call_args.kwargs["metrics_summary"],
            mode="fluency",
            topic="water",
            story_words=["water", "clean"],
            role="member",
        )

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_persists_session(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="fluency",
            duration=18.0,
        )

        cur = mock_conn.return_value.cursor()
        calls = [c[0][0] for c in cur.execute.call_args_list]
        assert any("INSERT INTO sessions" in c for c in calls)

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_persists_metrics(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="fluency",
            duration=18.0,
        )

        cur = mock_conn.return_value.cursor()
        calls = [c[0][0] for c in cur.execute.call_args_list]
        assert any("INSERT INTO metrics" in c for c in calls)

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_persists_feedback(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="fluency",
            duration=18.0,
        )

        cur = mock_conn.return_value.cursor()
        calls = [c[0][0] for c in cur.execute.call_args_list]
        assert any("INSERT INTO feedback" in c for c in calls)

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_commits_on_success(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="fluency",
            duration=18.0,
        )

        mock_conn.return_value.commit.assert_called_once()

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_closes_connection(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="fluency",
            duration=18.0,
        )

        mock_conn.return_value.close.assert_called_once()

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_stores_feedback_as_json(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="fluency",
            duration=18.0,
        )

        cur = mock_conn.return_value.cursor()
        for call_args in cur.execute.call_args_list:
            args = call_args[0]
            if "INSERT INTO feedback" in args[0]:
                params = args[1]
                assert isinstance(params[3], str)  # strengths as JSON
                assert json.loads(params[3]) == sample_feedback["strengths"]
                break
        else:
            pytest.fail("No feedback INSERT call found")


# -- Tests: error handling -- #


class TestRunAnalysisErrors:
    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_llm_error_raises_orchestration_error(self, mock_conn, mock_llm, sample_transcript):
        from services.llm_service import LLMError
        mock_llm.side_effect = LLMError("API failed")
        mock_conn.return_value = MagicMock()

        with pytest.raises(OrchestrationError, match="LLM feedback failed"):
            run_analysis(
                user_id="user-123",
                transcript=sample_transcript,
                mode="fluency",
                duration=18.0,
            )

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_db_error_rolls_back(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()
        mock_conn.return_value.cursor.return_value.execute.side_effect = Exception("DB error")

        with pytest.raises(OrchestrationError, match="DB storage failed"):
            run_analysis(
                user_id="user-123",
                transcript=sample_transcript,
                mode="fluency",
                duration=18.0,
            )

        mock_conn.return_value.rollback.assert_called_once()
        mock_conn.return_value.close.assert_called_once()

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_connection_closed_after_error(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()
        mock_conn.return_value.cursor.return_value.execute.side_effect = Exception("DB crash")

        with pytest.raises(OrchestrationError):
            run_analysis(
                user_id="user-123",
                transcript=sample_transcript,
                mode="fluency",
                duration=18.0,
            )

        mock_conn.return_value.close.assert_called_once()


# -- Tests: edge cases -- #


class TestRunAnalysisEdgeCases:
    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_story_mode_with_story_words(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        result = run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="story",
            story_words=["adventure", "dragon"],
            duration=18.0,
        )

        assert result.story_words == ["adventure", "dragon"]

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_audio_url_passed_through(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        result = run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="fluency",
            audio_url="https://example.com/audio.mp3",
            duration=18.0,
        )

        assert result.audio_url == "https://example.com/audio.mp3"

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_role_passed_through(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        result = run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="fluency",
            role="teacher",
            duration=18.0,
        )

        assert result.role == "teacher"

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_topic_passed_through(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        result = run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="topic",
            topic="climate change",
            duration=18.0,
        )

        assert result.topic == "climate change"

    @patch("services.analysis_orchestrator.get_llm_feedback")
    @patch("services.analysis_orchestrator.get_connection")
    def test_default_duration_zero(self, mock_conn, mock_llm, sample_transcript, sample_feedback):
        mock_llm.return_value = sample_feedback
        mock_conn.return_value = MagicMock()

        result = run_analysis(
            user_id="user-123",
            transcript=sample_transcript,
            mode="fluency",
        )

        assert result.mode == "fluency"


# -- Tests: result object -- #


class TestAnalysisResult:
    def test_contains_all_fields(self):
        result = AnalysisResult(
            session_id="s-123",
            user_id="u-456",
            mode="fluency",
            metrics={"word_count": 50},
            feedback={"overall_score": 8},
        )

        assert result.session_id == "s-123"
        assert result.user_id == "u-456"
        assert result.mode == "fluency"
        assert result.metrics["word_count"] == 50
        assert result.feedback["overall_score"] == 8

    def test_optional_fields_default_to_none(self):
        result = AnalysisResult(
            session_id="s-123",
            user_id="u-456",
            mode="fluency",
            metrics={},
            feedback={},
        )

        assert result.audio_url is None
        assert result.topic is None
        assert result.story_words is None
        assert result.role is None
