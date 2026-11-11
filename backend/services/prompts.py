"""Prompt templates for LLM speech feedback.

Each mode has its own prompt template tailored to the evaluation criteria.
"""

from __future__ import annotations

from typing import Any


SYSTEM_INSTRUCTION = (
    "You are a supportive speech coach evaluating a student's spoken English. "
    "Analyze the transcript and metrics to provide constructive, specific feedback. "
    "Respond ONLY with a JSON object matching the specified format. No markdown, no explanation."
)


def build_output_format() -> str:
    return (
        "Output format (JSON only, no markdown):\n"
        "```\n"
        "{\n"
        '  "strengths": ["string", ...],\n'
        '  "areas_for_improvement": ["string", ...],\n'
        '  "score": 0.0-10.0,\n'
        '  "score_breakdown": {\n'
        '    "pronunciation": 0.0-10.0,\n'
        '    "fluency": 0.0-10.0,\n'
        '    "vocabulary": 0.0-10.0,\n'
        '    "grammar": 0.0-10.0\n'
        "  },\n"
        '  "specific_suggestions": ["string", ...]\n'
        "}\n"
        "```"
    )


# ── Mode-specific prompts ────────────────────────────────────


def get_impromptu_prompt(transcript: str, metrics_summary: str, topic: str | None) -> str:
    parts = [f"Mode: Impromptu Speech — The student spoke without preparation."]
    if topic:
        parts.append(f"Topic: {topic}")
    parts.append(f"Transcript:\n{transcript}")
    parts.append(f"Metrics: {metrics_summary}")
    parts.append(
        "Focus on: ability to think on the spot, coherence without preparation, "
        "natural pacing, and use of filler words."
    )
    return "\n\n".join(parts)


def get_table_topics_prompt(transcript: str, metrics_summary: str, topic: str | None) -> str:
    parts = [
        "Mode: Table Topics — The student received a random topic card and spoke on it.",
        f"Topic: {topic or 'Unspecified'}",
        f"Transcript:\n{transcript}",
        f"Metrics: {metrics_summary}",
        "Focus on: relevance to the given topic, organization of thoughts under time pressure, "
        "and ability to stay on topic for the full duration.",
    ]
    return "\n\n".join(parts)


def get_storytelling_prompt(transcript: str, metrics_summary: str, story_words: list[str] | None) -> str:
    parts = [
        "Mode: Storytelling — The student told a story.",
        f"Transcript:\n{transcript}",
        f"Metrics: {metrics_summary}",
        "Focus on: narrative structure (beginning, middle, end), creativity, "
        "emotional engagement, descriptive language, and coherence of the story.",
    ]
    if story_words:
        parts.insert(3, f"Required words: {', '.join(story_words)}")
        parts.append("Check whether all required words were used naturally in the story.")
    return "\n\n".join(parts)


def get_prepared_speech_prompt(transcript: str, metrics_summary: str, topic: str | None) -> str:
    parts = [
        "Mode: Prepared Speech — The student prepared and delivered a speech in advance.",
        f"Topic: {topic or 'Unspecified'}",
        f"Transcript:\n{transcript}",
        f"Metrics: {metrics_summary}",
        "Focus on: delivery quality, memorization vs reading, confidence, "
        "audience engagement, and the overall impact of the prepared speech.",
    ]
    return "\n\n".join(parts)


def get_evaluations_prompt(
    transcript: str, metrics_summary: str, topic: str | None, role: str | None
) -> str:
    parts = [
        "Mode: Evaluations Speech — The student gave a formal speech in a competition-style format.",
        f"Topic: {topic or 'Unspecified'}",
        f"Role: {role or 'General'}",
        f"Transcript:\n{transcript}",
        f"Metrics: {metrics_summary}",
        "Focus on: formal address style (opening to judges/audience), structured argument, "
        "clarity of the central message, rhetorical devices, and closing impact.",
    ]
    return "\n\n".join(parts)


# ── Mode dispatch ─────────────────────────────────────────────


MODE_PROMPTS = {
    "impromptu": get_impromptu_prompt,
    "table_topics": get_table_topics_prompt,
    "storytelling": get_storytelling_prompt,
    "prepared_speech": get_prepared_speech_prompt,
    "evaluations": get_evaluations_prompt,
}


def generate_full_prompt(
    mode: str,
    transcript: str,
    metrics_summary: str,
    extra_params: dict[str, Any] | None = None,
) -> str:
    """Build the full user prompt for a given mode."""
    extra = extra_params or {}
    prompt_fn = MODE_PROMPTS.get(mode)
    if not prompt_fn:
        raise ValueError(f"Unknown mode: {mode}")

    if mode == "impromptu":
        return prompt_fn(transcript, metrics_summary, extra.get("topic"))
    elif mode == "table_topics":
        return prompt_fn(transcript, metrics_summary, extra.get("topic"))
    elif mode == "storytelling":
        return prompt_fn(transcript, metrics_summary, extra.get("story_words"))
    elif mode == "prepared_speech":
        return prompt_fn(transcript, metrics_summary, extra.get("topic"))
    elif mode == "evaluations":
        return prompt_fn(transcript, metrics_summary, extra.get("topic"), extra.get("role"))
    return ""
