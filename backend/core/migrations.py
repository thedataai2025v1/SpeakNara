"""Apply SQL migrations against the local SQLite database."""

from pathlib import Path

from .database import get_connection
from .settings import settings


MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def apply_migrations() -> list[str]:
    """Run all SQL migration files (sorted) and return the applied file names."""
    applied: list[str] = []
    conn = get_connection()
    try:
        for file_path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            sql = file_path.read_text(encoding="utf-8")
            conn.executescript(sql)
            applied.append(file_path.name)
    finally:
        conn.close()
    return applied
