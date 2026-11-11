"""Table Topics endpoint — generates a topic with keywords and time limit."""

import random
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class TopicResponse(BaseModel):
    topic: str
    keywords: list[str]
    time_limit: int  # seconds


router = APIRouter(tags=["table-topics"])

# Predefined topics with keywords for deterministic, offline generation
TOPICS = [
    {"topic": "Describe your favourite childhood memory", "keywords": ["memory", "childhood", "emotion"]},
    {"topic": "If you could have any superpower, what would it be?", "keywords": ["superpower", "choice", "reason"]},
    {"topic": "What makes a good leader?", "keywords": ["leader", "trait", "example"]},
    {"topic": "Describe your ideal day from morning to night", "keywords": ["day", "routine", "relax"]},
    {"topic": "What book changed your life and why?", "keywords": ["book", "change", "reason"]},
    {"topic": "Explain your hometown to someone visiting for the first time", "keywords": ["hometown", "place", "culture"]},
    {"topic": "What is the most important lesson you have learned?", "keywords": ["lesson", "experience", "growth"]},
    {"topic": "Describe a time you faced a difficult challenge", "keywords": ["challenge", "overcome", "learn"]},
    {"topic": "What technology do you think will change the world most?", "keywords": ["technology", "future", "impact"]},
    {"topic": "If you could travel anywhere, where would you go?", "keywords": ["travel", "place", "reason"]},
    {"topic": "Describe your favourite meal", "keywords": ["food", "flavour", "memory"]},
    {"topic": "What skill would you like to learn and why?", "keywords": ["skill", "learn", "reason"]},
    {"topic": "Talk about a person who inspires you", "keywords": ["person", "inspire", "quality"]},
    {"topic": "What is your favourite season and why?", "keywords": ["season", "weather", "activity"]},
    {"topic": "Describe the best gift you have ever received", "keywords": ["gift", "surprise", "value"]},
    {"topic": "What problem in your community would you like to solve?", "keywords": ["community", "problem", "solution"]},
    {"topic": "If you could meet any historical figure, who would it be?", "keywords": ["history", "person", "question"]},
    {"topic": "Describe your dream job", "keywords": ["job", "passion", "work"]},
    {"topic": "What is the best advice you have ever received?", "keywords": ["advice", "wisdom", "follow"]},
    {"topic": "Talk about a tradition important to your family", "keywords": ["tradition", "family", "meaning"]},
]

# Time limits by difficulty (seconds)
TIME_LIMITS = [60, 90, 120, 180]


@router.post("/generate", response_model=TopicResponse)
def generate_topic():
    """Generate a random Table Topic with keywords and time limit."""
    topic_entry = random.choice(TOPICS)
    time_limit = random.choice(TIME_LIMITS)
    return TopicResponse(
        topic=topic_entry["topic"],
        keywords=topic_entry["keywords"],
        time_limit=time_limit,
    )
