"""LLM service for speech feedback using Euron API."""

from __future__ import annotations

import json
import time
from typing import Any

from openai import APIStatusError, OpenAI

from core.settings import settings
from services import prompts


class LLMError(Exception):
    """Raised when the LLM API call fails or returns invalid data."""


def _client() -> OpenAI:
    return OpenAI(
        api_key=settings.euri_api_key,
        base_url=settings.llm_base_url,
    )


MAX_RETRIES = 3
RETRY_DELAY = 1.0


def get_llm_feedback(
    transcript: str,
    metrics_summary: str,
    mode: str,
    topic: str | None = None,
    story_words: list[str] | None = None,
    role: str | None = None,
) -> dict[str, Any]:
    """Call the LLM to evaluate a speech and return structured feedback.

    Args:
        transcript: The transcribed speech text.
        metrics_summary: Human-readable metrics (WPM, pauses, filler words).
        mode: One of impromptu, table_topics, storytelling, prepared_speech, evaluations.
        topic: Topic name (for modes that use it).
        story_words: List of required words (for storytelling mode).
        role: Speech role (for evaluations mode).

    Returns:
        Dict with keys: strengths, areas_for_improvement, score, score_breakdown, specific_suggestions.

    Raises:
        LLMError: On API failure, invalid response, or missing required fields.
    """
    extra = {"topic": topic, "story_words": story_words, "role": role}
    try:
        user_content = prompts.generate_full_prompt(
            mode, transcript, metrics_summary, extra,
        )
    except ValueError as exc:
        raise LLMError(str(exc)) from exc

    client = _client()
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": prompts.SYSTEM_INSTRUCTION + "\n\n" + prompts.build_output_format()},
                    {"role": "user", "content": user_content},
                ],
                max_tokens=1500,
                temperature=0.7,
            )

            if not response.choices:
                raise LLMError("LLM response is empty")

            raw = response.choices[0].message.content
            if not raw:
                raise LLMError("LLM response content is empty")

            try:
                feedback = json.loads(raw)
            except json.JSONDecodeError:
                raise LLMError("LLM returned invalid JSON") from last_error

            required = ["score", "strengths", "areas_for_improvement", "score_breakdown", "specific_suggestions"]
            missing = [k for k in required if k not in feedback]
            if missing:
                raise LLMError(f"LLM feedback missing fields: {', '.join(missing)}")

            return feedback

        except APIStatusError as exc:
            if exc.status_code == 429 and attempt < MAX_RETRIES - 1:
                last_error = exc
                time.sleep(RETRY_DELAY)
                continue
            raise LLMError(f"LLM API error: {exc.message}") from exc
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError(f"Unexpected LLM error: {exc}") from exc

    raise LLMError("Max retries exceeded")
