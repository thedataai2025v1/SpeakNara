"""Local SQLite database utilities."""

from __future__ import annotations

import sqlite3
from typing import Generator

from .settings import settings


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a SQLite connection using DATABASE_URL from settings."""
    conn = sqlite3.connect(settings.database_url.replace("sqlite:///", ""))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_connection() -> sqlite3.Connection:
    """Return a direct (non-context-manager) SQLite connection."""
    conn = sqlite3.connect(settings.database_url.replace("sqlite:///", ""))
    conn.row_factory = sqlite3.Row
    return conn
