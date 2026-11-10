"""Seed the local SQLite database with sample data (idempotent).

Run after migrations have created the tables.  Existing rows are never
overwritten so the script is safe to call multiple times.
"""

from __future__ import annotations

import uuid
from typing import Generator

from .database import get_db

# ── Seed data ────────────────────────────────────────────────

TOPICS = [
    {"title": "Greetings",        "language": "en", "level": "A1"},
    {"title": "Introductions",    "language": "en", "level": "A1"},
    {"title": "Numbers",          "language": "en", "level": "A1"},
    {"title": "Colours",          "language": "en", "level": "A1"},
    {"title": "Days and times",   "language": "en", "level": "A1"},
    {"title": "Family",           "language": "en", "level": "A1"},
    {"title": "Food and drink",   "language": "en", "level": "A1"},
    {"title": "Shopping",         "language": "en", "level": "A1"},
    {"title": "Weather",          "language": "en", "level": "A1"},
    {"title": "Home and furniture","language": "en", "level": "A1"},
    {"title": "Body parts",       "language": "en", "level": "A2"},
    {"title": "Clothes",          "language": "en", "level": "A2"},
    {"title": "Transport",        "language": "en", "level": "A2"},
    {"title": "Cities and places","language": "en", "level": "A2"},
    {"title": "Daily routines",   "language": "en", "level": "A2"},
    {"title": "Hobbies",          "language": "en", "level": "A2"},
    {"title": "Health",           "language": "en", "level": "A2"},
    {"title": "School",           "language": "en", "level": "A2"},
    {"title": "Jobs and careers", "language": "en", "level": "A2"},
    {"title": "Feelings",         "language": "en", "level": "B1"},
    {"title": "Relationships",    "language": "en", "level": "B1"},
    {"title": "Travel plans",     "language": "en", "level": "B1"},
    {"title": "News and media",   "language": "en", "level": "B1"},
    {"title": "Environment",      "language": "en", "level": "B1"},
    {"title": "Culture",          "language": "en", "level": "B1"},
    {"title": "Education",        "language": "en", "level": "B1"},
    {"title": "Money and finance","language": "en", "level": "B2"},
    {"title": "Technology",       "language": "en", "level": "B2"},
    {"title": "Politics",         "language": "en", "level": "B2"},
    {"title": "Science",          "language": "en", "level": "B2"},
]

WORDS: list[dict] = [
    # Greetings (topic_id filled in at seed time)
    {"word": "Hello",        "meaning": "A greeting used when meeting someone"},
    {"word": "Goodbye",      "meaning": "A farewell expression"},
    {"word": "Welcome",      "meaning": "Used to greet someone warmly"},
    {"word": "Thanks",       "meaning": "Used to express gratitude"},
    {"word": "Please",       "meaning": "Used to make polite requests"},
    # Introductions
    {"word": "Name",         "meaning": "What you are called"},
    {"word": "Age",          "meaning": "How long you have lived"},
    {"word": "Country",      "meaning": "The nation you come from"},
    # Numbers
    {"word": "One",          "meaning": "The number 1"},
    {"word": "Ten",          "meaning": "The number 10"},
    {"word": "Hundred",      "meaning": "The number 100"},
    # Colours
    {"word": "Red",          "meaning": "A primary colour"},
    {"word": "Blue",         "meaning": "A primary colour"},
    {"word": "Green",        "meaning": "A secondary colour"},
    {"word": "Yellow",       "meaning": "A secondary colour"},
    # Days and times
    {"word": "Monday",       "meaning": "First weekday"},
    {"word": "Friday",       "meaning": "Last weekday"},
    {"word": "Weekend",      "meaning": "Days after work/school week"},
    # Family
    {"word": "Mother",       "meaning": "Female parent"},
    {"word": "Father",       "meaning": "Male parent"},
    {"word": "Sister",       "meaning": "Female sibling"},
    # Food and drink
    {"word": "Water",        "meaning": "A clear drinking liquid"},
    {"word": "Bread",        "meaning": "A baked grain food"},
    {"word": "Coffee",       "meaning": "A hot caffeinated drink"},
    # Shopping
    {"word": "Price",        "meaning": "How much something costs"},
    {"word": "Discount",     "meaning": "A reduction in price"},
    # Weather
    {"word": "Rain",         "meaning": "Water falling from clouds"},
    {"word": "Sunshine",     "meaning": "Light from the sun"},
    {"word": "Snow",         "meaning": "Frozen precipitation"},
    # Home and furniture
    {"word": "Table",        "meaning": "A flat surface on legs"},
    {"word": "Chair",        "meaning": "A seat with a back"},
    # Transport
    {"word": "Bus",          "meaning": "A large public vehicle"},
    {"word": "Train",        "meaning": "A rail vehicle"},
    {"word": "Airport",      "meaning": "Place where planes take off and land"},
    # Daily routines
    {"word": "Wake",         "meaning": "To stop sleeping"},
    {"word": "Eat",          "meaning": "To consume food"},
    {"word": "Sleep",        "meaning": "To rest at night"},
    # Hobbies
    {"word": "Reading",      "meaning": "The activity of reading books"},
    {"word": "Cooking",      "meaning": "Preparing food"},
    {"word": "Gardening",    "meaning": "Growing plants"},
    # Health
    {"word": "Doctor",       "meaning": "A medical professional"},
    {"word": "Medicine",     "meaning": "Substance for treating illness"},
    # Jobs and careers
    {"word": "Teacher",      "meaning": "Someone who educates"},
    {"word": "Engineer",     "meaning": "Someone who designs systems"},
    # Feelings
    {"word": "Happy",        "meaning": "Feeling pleasure"},
    {"word": "Sad",          "meaning": "Feeling sorrow"},
    {"word": "Angry",        "meaning": "Feeling strong displeasure"},
    # Travel plans
    {"word": "Ticket",       "meaning": "A document granting travel"},
    {"word": "Hotel",        "meaning": "A place to stay while travelling"},
    # Environment
    {"word": "Forest",       "meaning": "An area of trees"},
    {"word": "Ocean",        "meaning": "A large body of salt water"},
    # Technology
    {"word": "Computer",     "meaning": "An electronic device for processing data"},
    {"word": "Internet",     "meaning": "A global network of computers"},
    {"word": "Phone",        "meaning": "A portable communication device"},
]


def _get_db():
    """Return a connection that auto-commits (for simple inserts)."""
    from .database import get_connection
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _upsert_users(conn) -> None:
    """Insert a demo user if not present (idempotent)."""
    demo_id = "550e8400-e29b-41b4-941e-001a00000001"
    existing = conn.execute("SELECT id FROM users WHERE id = ?", (demo_id,)).fetchone()
    if existing:
        return
    conn.execute(
        "INSERT INTO users (id, email, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
        (demo_id, "demo@speaknara.com", "Demo User", "learner", "2026-01-01T00:00:00Z"),
    )


def _upsert_topics(conn) -> dict:
    """Insert topics if they don't already exist. Return {title: id} map."""
    title_to_id: dict[str, int] = {}
    for i, t in enumerate(TOPICS):
        existing = conn.execute(
            "SELECT id FROM topics WHERE title = ? AND language = ?",
            (t["title"], t["language"]),
        ).fetchone()
        if existing:
            title_to_id[t["title"]] = existing["id"]
            continue
        conn.execute(
            "INSERT INTO topics (title, description, language, level, sort_order) VALUES (?, ?, ?, ?, ?)",
            (t["title"], f"Lesson about {t['title'].lower()}", t["language"], t["level"], i + 1),
        )
        title_to_id[t["title"]] = conn.execute("SELECT last_insert_rowid()").fetchone()["last_insert_rowid()"]
    return title_to_id


def _upsert_words(conn, title_to_id: dict) -> None:
    """Insert words linked to the matching topic (idempotent by word + topic_id)."""
    # Group words by topic (every TOPICS[i] gets WORDS[i*2:i*2+2] pattern won't work
    # so we simply cycle words across topics in order)
    topic_ids = [title_to_id[t["title"]] for t in TOPICS]
    for idx, w in enumerate(WORDS):
        topic_idx = idx % len(topic_ids)  # spread across topics
        topic_id = topic_ids[topic_idx]
        existing = conn.execute(
            "SELECT id FROM random_words WHERE word = ? AND topic_id = ?",
            (w["word"], topic_id),
        ).fetchone()
        if existing:
            continue
        conn.execute(
            "INSERT INTO random_words (topic_id, word, meaning, language) VALUES (?, ?, ?, ?)",
            (topic_id, w["word"], w["meaning"], "en"),
        )


def seed() -> dict:
    """Run all seed operations. Returns counts dict."""
    conn = _get_db()
    try:
        _upsert_users(conn)
        title_to_id = _upsert_topics(conn)
        _upsert_words(conn, title_to_id)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    conn2 = _get_db()
    try:
        return {
            "users": _count(conn2, "users"),
            "topics": _count(conn2, "topics"),
            "random_words": _count(conn2, "random_words"),
        }
    finally:
        conn2.close()


def _count(conn, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


# Allow running as a script: `python -m backend.core.seed`
if __name__ == "__main__":
    print("Applying migrations first …")
    from .migrations import apply_migrations  # noqa: F401
    apply_migrations()
    result = seed()
    print(f"Seeded: {result}")
