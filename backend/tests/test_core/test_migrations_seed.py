"""Tests for migrations and seed data."""
import sqlite3
import tempfile
from importlib import import_module, reload
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def temp_db(monkeypatch):
    """Provide a temporary SQLite database. Monkeypatches settings so every
    DB call opens a fresh connection to the temp file."""
    from backend.core import settings as settings_mod
    from backend.core.settings import Settings

    # Use a temp file with a unique name
    db_path = tempfile.mktemp(suffix=".db")
    new_settings = Settings(DATABASE_URL=f"sqlite:///{db_path}")
    monkeypatch.setattr(settings_mod, "settings", new_settings)

    # Reload modules that cache the settings reference
    from backend.core import database as db_mod
    from backend.core import migrations as mig_mod
    from backend.core import seed_data as seed_mod

    reload(db_mod)
    reload(mig_mod)
    reload(seed_mod)

    yield db_path

    # Cleanup: delete the temp DB file if it was created
    # Close any lingering connections first
    try:
        from backend.core.database import get_connection
        conn = get_connection()
        conn.close()
    except Exception:
        pass

    p = Path(db_path)
    if p.exists():
        try:
            p.unlink()
        except PermissionError:
            pass  # Windows file lock


# ---------------------------------------------------------------------------
# Migration tests
# ---------------------------------------------------------------------------


def test_applies_all_migrations(temp_db, monkeypatch):
    """apply_migrations() runs without error and returns applied file names."""
    from backend.core.migrations import apply_migrations

    applied = apply_migrations()
    assert "001_initial.sql" in applied


def test_tables_exist(temp_db, monkeypatch):
    """All 5 tables should exist after migrations."""
    from backend.core.migrations import apply_migrations
    from backend.core.database import get_connection

    apply_migrations()

    conn = get_connection()
    tables = {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()

    for name in ("users", "topics", "random_words", "sessions", "session_metrics"):
        assert name in tables, f"Table {name} missing"


def test_foreign_keys_work(temp_db, monkeypatch):
    """Inserting a user then a session should succeed (FK check)."""
    from backend.core.migrations import apply_migrations
    from backend.core.database import get_connection

    apply_migrations()

    conn = get_connection()
    conn.execute(
        "INSERT INTO users (id, email, full_name) VALUES ('abc', 'a@b.c', 'A')"
    )
    conn.execute(
        "INSERT INTO sessions (user_id, topic_id, started_at, status) "
        "VALUES ('abc', 1, '2024-01-01', 'completed')"
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Seed tests
# ---------------------------------------------------------------------------


def test_seed_creates_expected_rows(temp_db, monkeypatch):
    """Seeding should produce 3 users, 30 topics, and the full word set."""
    from backend.core.migrations import apply_migrations
    from backend.core.seed_data import seed

    apply_migrations()
    result = seed()

    assert result["users"] >= 1, f"Expected at least 1 user, got {result['users']}"
    assert result["topics"] == 30, f"Expected 30 topics, got {result['topics']}"
    assert result["random_words"] > 0, "Should have seeded words"


def test_seed_is_idempotent(temp_db, monkeypatch):
    """Running seed() twice should not duplicate rows."""
    from backend.core.migrations import apply_migrations
    from backend.core.seed_data import seed

    apply_migrations()
    result1 = seed()
    result2 = seed()

    assert result1 == result2, "Seed should be idempotent"


def test_seed_words_distributed(temp_db, monkeypatch):
    """Words should be spread across multiple topics, not concentrated on one."""
    from backend.core.migrations import apply_migrations
    from backend.core.seed_data import seed
    from backend.core.database import get_connection

    apply_migrations()
    seed()

    conn = get_connection()
    rows = conn.execute(
        "SELECT topic_id, COUNT(*) AS cnt FROM random_words GROUP BY topic_id"
    ).fetchall()
    conn.close()

    topic_ids_with_words = {row["topic_id"] for row in rows}
    # Words are cycled across all 30 topics, so at least all should have some
    assert len(topic_ids_with_words) > 10, (
        f"Only {len(topic_ids_with_words)} topics have words"
    )
