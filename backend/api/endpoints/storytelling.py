"""Storytelling endpoint — generates a story prompt with words and time limit."""

import random
from fastapi import APIRouter
from pydantic import BaseModel


class StoryPromptResponse(BaseModel):
    prompt: str
    story_words: list[str]
    time_limit: int  # seconds


router = APIRouter(tags=["storytelling"])

# Story prompts
STORY_PROMPTS = [
    "Tell a story that starts with 'It all began on a rainy Tuesday...'",
    "Tell a story about finding something unexpected in an old pocket.",
    "Tell a story about a journey that changes everything.",
    "Tell a story about the last person on Earth hearing a knock at the door.",
    "Tell a story about discovering a door in your house that wasn't there before.",
    "Tell a story about a letter you receive from your future self.",
    "Tell a story about the day gravity stopped working for just one minute.",
    "Tell a story about a conversation with someone you thought you'd never see again.",
    "Tell a story about losing something and finding something better.",
    "Tell a story about a small act of kindness that changed the world.",
    "Tell a story about waking up in a world where everyone speaks a different language.",
    "Tell a story about the most important decision you ever made.",
    "Tell a story about an object that holds a lifetime of memories.",
    "Tell a story about meeting someone who looks exactly like you.",
    "Tell a story about a place where time stands still.",
]

# Random words that must be included in the story
STORY_WORD_POOLS = [
    ["bridge", "whisper", "forgotten", "light"],
    ["shadow", "promise", "ocean", "key"],
    ["mountain", "secret", "song", "map"],
    ["river", "memory", "door", "flame"],
    ["star", "journey", "voice", "path"],
    ["garden", "truth", "storm", "peace"],
    ["clock", "mirror", "letter", "bridge"],
    ["window", "garden", "whisper", "stone"],
    ["candle", "shadow", "music", "dream"],
    ["island", "compass", "legend", "tide"],
]


@router.post("/generate", response_model=StoryPromptResponse)
def generate_story_prompt():
    """Generate a random storytelling prompt with required words and time limit."""
    prompt = random.choice(STORY_PROMPTS)
    story_words = random.choice(STORY_WORD_POOLS)
    # Storytelling typically has longer time limits
    time_limit = random.choice([120, 180, 240, 300])
    return StoryPromptResponse(
        prompt=prompt,
        story_words=story_words,
        time_limit=time_limit,
    )
