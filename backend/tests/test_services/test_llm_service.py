"""Tests for LLM service (Euron API integration)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from openai import APIStatusError


class MockChoice:
    """Mock OpenAI choice object."""

    def __init__(self, content):
        self.message = MagicMock()
        self.message.content = content


class MockResponse:
    """Mock OpenAI chat completion response."""

    def __init__(self, content):
        self.choices = [MockChoice(content)]
        self.model = "claude-sonnet-5-5"
        self.id = "chatcmpl-test"


def mock_feedback_json():
    return json.dumps({
        "strengths": ["Good pace", "Clear pronunciation"],
        "areas_for_improvement": ["Work on fluency"],
        "score": 7.5,
        "score_breakdown": {
            "pronunciation": 8.0,
            "fluency": 7.0,
            "vocabulary": 7.5,
            "grammar": 8.0,
        },
        "specific_suggestions": ["Slow down during complex sentences"],
    })


# ── Prompt templates ──────────────────────────────────────────


def test_prompt_templates_exist():
    from services.prompts import MODE_PROMPTS
    for mode in ("impromptu", "table_topics", "storytelling", "prepared_speech", "evaluations"):
        assert mode in MODE_PROMPTS, f"{mode} not in MODE_PROMPTS"


def test_impromptu_prompt_structure():
    from services.prompts import get_impromptu_prompt
    prompt = get_impromptu_prompt(
        transcript="Hello world",
        metrics_summary="wpm: 120",
        topic=None,
    )
    assert "Hello world" in prompt
    assert "120" in prompt


def test_table_topics_prompt_includes_topic():
    from services.prompts import get_table_topics_prompt
    prompt = get_table_topics_prompt(
        transcript="Speech text",
        metrics_summary="wpm: 100",
        topic="Climate Change",
    )
    assert "Climate Change" in prompt


def test_storytelling_prompt_includes_words():
    from services.prompts import get_storytelling_prompt
    prompt = get_storytelling_prompt(
        transcript="Once upon a time",
        metrics_summary="wpm: 110",
        story_words=["dragon", "castle", "bridge"],
    )
    assert "dragon" in prompt.lower()
    assert "castle" in prompt.lower()


def test_prepared_speech_prompt():
    from services.prompts import get_prepared_speech_prompt
    prompt = get_prepared_speech_prompt(
        transcript="I have prepared a speech",
        metrics_summary="wpm: 130",
        topic="Annual Report",
    )
    assert "Annual Report" in prompt


def test_evaluations_prompt_has_judges():
    from services.prompts import get_evaluations_prompt
    prompt = get_evaluations_prompt(
        transcript="Honorable judges",
        metrics_summary="wpm: 125",
        topic="Education",
        role="Informative",
    )
    assert "Honorable judges" in prompt or "judges" in prompt.lower()


def test_generate_full_prompt_assembles_all_parts():
    from services.prompts import generate_full_prompt
    prompt = generate_full_prompt(
        mode="impromptu",
        transcript="Test transcript",
        metrics_summary="wpm: 120",
        extra_params={"topic": "AI"},
    )
    assert "Test transcript" in prompt
    assert "impromptu" in prompt.lower()


# ── LLM service ──────────────────────────────────────────────


def test_get_feedback_success():
    with patch("services.llm_service.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = MockResponse(mock_feedback_json())

        from services.llm_service import get_llm_feedback
        result = get_llm_feedback(
            transcript="Hello world",
            metrics_summary="wpm: 120",
            mode="impromptu",
        )
        assert result["score"] == 7.5
        assert len(result["strengths"]) == 2
        assert len(result["areas_for_improvement"]) == 1
        assert len(result["specific_suggestions"]) == 1
        assert "pronunciation" in result["score_breakdown"]
        mock_client.chat.completions.create.assert_called_once()


def test_get_feedback_calls_with_correct_model():
    with patch("services.llm_service.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = MockResponse(mock_feedback_json())

        from services.llm_service import get_llm_feedback
        get_llm_feedback("Transcript", "wpm: 100", "impromptu")
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "claude-sonnet-5-5"


def test_get_feedback_uses_correct_base_url():
    with patch("services.llm_service.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = MockResponse(mock_feedback_json())

        from services.llm_service import get_llm_feedback
        get_llm_feedback("Transcript", "wpm: 100", "impromptu")
        assert mock_openai_cls.call_args[1]["base_url"] == "https://api.euron.one/api/v1/euri"


def test_get_feedback_handles_api_error():
    with patch("services.llm_service.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        error = APIStatusError(
            message="API error",
            response=MagicMock(),
            body={},
        )
        error.status_code = 500
        mock_client.chat.completions.create.side_effect = error

        from services.llm_service import get_llm_feedback, LLMError
        with pytest.raises(LLMError, match="API error"):
            get_llm_feedback("Transcript", "wpm: 100", "impromptu")


def test_get_feedback_retries_on_429():
    with patch("services.llm_service.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        err = APIStatusError(message="Rate limit", response=MagicMock(), body={})
        err.status_code = 429
        mock_client.chat.completions.create.side_effect = [err, MockResponse(mock_feedback_json())]

        from services.llm_service import get_llm_feedback
        result = get_llm_feedback("Transcript", "wpm: 100", "impromptu")
        assert result["score"] == 7.5
        assert mock_client.chat.completions.create.call_count == 2


def test_get_feedback_gives_up_after_max_retries():
    with patch("services.llm_service.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        err = APIStatusError(message="Rate limit", response=MagicMock(), body={})
        err.status_code = 429
        mock_client.chat.completions.create.side_effect = err

        from services.llm_service import get_llm_feedback, LLMError
        with pytest.raises(LLMError):
            get_llm_feedback("Transcript", "wpm: 100", "impromptu")


def test_get_feedback_invalid_json():
    with patch("services.llm_service.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = MockResponse("not json {")

        from services.llm_service import get_llm_feedback, LLMError
        with pytest.raises(LLMError, match="invalid JSON"):
            get_llm_feedback("Transcript", "wpm: 100", "impromptu")


def test_get_feedback_missing_score():
    with patch("services.llm_service.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        bad = json.dumps({"strengths": [], "areas_for_improvement": []})
        mock_client.chat.completions.create.return_value = MockResponse(bad)

        from services.llm_service import get_llm_feedback, LLMError
        with pytest.raises(LLMError, match="missing"):
            get_llm_feedback("Transcript", "wpm: 100", "impromptu")


def test_get_feedback_with_topic():
    with patch("services.llm_service.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = MockResponse(mock_feedback_json())

        from services.llm_service import get_llm_feedback
        get_llm_feedback("Transcript", "wpm: 100", "table_topics", topic="AI Ethics")
        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        assert "AI Ethics" in messages[1]["content"]


def test_get_feedback_with_story_words():
    with patch("services.llm_service.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = MockResponse(mock_feedback_json())

        from services.llm_service import get_llm_feedback
        get_llm_feedback("Transcript", "wpm: 100", "storytelling", story_words=["apple", "moon", "car"])
        messages = mock_client.chat.completions.create.call_args[1]["messages"]
        msg = messages[1]["content"]
        assert "apple" in msg.lower()


def test_get_feedback_unknown_mode():
    with patch("services.llm_service.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        from services.llm_service import get_llm_feedback, LLMError
        with pytest.raises(LLMError, match="Unknown mode"):
            get_llm_feedback("Transcript", "wpm: 100", "nonexistent_mode")


def test_get_feedback_empty_response():
    with patch("services.llm_service.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response

        from services.llm_service import get_llm_feedback, LLMError
        with pytest.raises(LLMError, match="empty"):
            get_llm_feedback("Transcript", "wpm: 100", "impromptu")
