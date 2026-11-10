-- 001_initial: Create the core tables for SpeakNara
-- Compatible with SQLite (for testing) and Supabase PostgreSQL

-- ---------------------------------------------------------------------------
-- Users: mirrors the Supabase auth.users subset we need locally
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id           TEXT PRIMARY KEY,
    email        TEXT UNIQUE NOT NULL,
    full_name    TEXT,
    role         TEXT NOT NULL DEFAULT 'learner' CHECK (role IN ('learner', 'teacher', 'admin')),
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ---------------------------------------------------------------------------
-- Topics: one row per language topic (unit/lesson)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS topics (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT,
    language    TEXT NOT NULL DEFAULT 'en',
    level       TEXT NOT NULL DEFAULT 'A1' CHECK (level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    sort_order  INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_topics_language ON topics(language);

-- ---------------------------------------------------------------------------
-- Random_words: vocabulary words attached to a topic
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS random_words (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id    INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    word        TEXT NOT NULL,
    meaning     TEXT NOT NULL,
    language    TEXT NOT NULL DEFAULT 'en',
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_random_words_topic_id ON random_words(topic_id);

-- ---------------------------------------------------------------------------
-- Sessions: one row per user practice session
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic_id    INTEGER REFERENCES topics(id) ON DELETE SET NULL,
    started_at  TEXT NOT NULL DEFAULT (datetime('now')),
    ended_at    TEXT,
    score       REAL,
    status      TEXT NOT NULL DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed', 'skipped')),
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);

-- ---------------------------------------------------------------------------
-- Session_metrics: key-value style metrics inside a session
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS session_metrics (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    key         TEXT NOT NULL,
    value       TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_session_metrics_session_id ON session_metrics(session_id);
