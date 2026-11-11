"""Prepared speech endpoint — generates speech topics for delivery practice."""

import random
from fastapi import APIRouter

router = APIRouter()

TOPICS = [
    "Give a motivational speech about perseverance",
    "Deliver a persuasive argument for renewable energy",
    "Present a eulogy for someone you admire",
    "Give a wedding toast for a close friend",
    "Present a vision for your community's future",
    "Deliver an inauguration address for a new organization",
    "Give a commencement speech to graduates",
    "Present a pitch for a social cause you believe in",
    "Deliver a speech defending free speech on campus",
    "Present a farewell address for a retiring leader",
]

KEYWORDS = [
    "gratitude", "challenge", "vision", "unity", "action",
    "hope", "legacy", "courage", "growth", "inspire",
    "commitment", "resilience", "opportunity", "change", "impact",
]


@router.post("/generate")
def generate():
    """Generate a prepared speech topic with keywords and a 120-second time limit."""
    topic = random.choice(TOPICS)
    keywords = random.sample(KEYWORDS, 3)
    return {
        "topic": topic,
        "keywords": keywords,
        "time_limit": 120,
    }
