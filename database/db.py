"""SQLite database layer for AI-Powered Study Buddy."""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Iterable

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they don't exist."""
    with get_conn() as conn:
        c = conn.cursor()
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                topic TEXT NOT NULL,
                studied_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS quiz_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                taken_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                topic TEXT NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS study_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subjects TEXT NOT NULL,
                exam_date TEXT NOT NULL,
                plan TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )

        # Ensure a default user exists
        c.execute("SELECT id FROM users WHERE username = ?", ("default",))
        if not c.fetchone():
            c.execute(
                "INSERT INTO users (username, created_at) VALUES (?, ?)",
                ("default", datetime.utcnow().isoformat()),
            )


def get_default_user_id() -> int:
    with get_conn() as conn:
        row = conn.execute("SELECT id FROM users WHERE username = 'default'").fetchone()
        return int(row["id"]) if row else 1


# --- Insert helpers -------------------------------------------------------

def log_topic(topic: str, user_id: int | None = None) -> None:
    user_id = user_id or get_default_user_id()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO topics (user_id, topic, studied_at) VALUES (?, ?, ?)",
            (user_id, topic, datetime.utcnow().isoformat()),
        )


def log_quiz(topic: str, difficulty: str, score: int, total: int,
             user_id: int | None = None) -> None:
    user_id = user_id or get_default_user_id()
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO quiz_history
               (user_id, topic, difficulty, score, total, taken_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, topic, difficulty, score, total,
             datetime.utcnow().isoformat()),
        )


def log_flashcards(topic: str, cards: Iterable[dict],
                   user_id: int | None = None) -> None:
    user_id = user_id or get_default_user_id()
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.executemany(
            """INSERT INTO flashcards (user_id, topic, front, back, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            [(user_id, topic, c["front"], c["back"], now) for c in cards],
        )


def log_study_plan(subjects: str, exam_date: str, plan: str,
                   user_id: int | None = None) -> None:
    user_id = user_id or get_default_user_id()
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO study_plans
               (user_id, subjects, exam_date, plan, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, subjects, exam_date, plan,
             datetime.utcnow().isoformat()),
        )


# --- Query helpers --------------------------------------------------------

def fetch_all(table: str):
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(f"SELECT * FROM {table}").fetchall()]


def get_stats() -> dict:
    with get_conn() as conn:
        topics_count = conn.execute("SELECT COUNT(*) AS n FROM topics").fetchone()["n"]
        quiz_count = conn.execute("SELECT COUNT(*) AS n FROM quiz_history").fetchone()["n"]
        avg = conn.execute(
            "SELECT AVG(CAST(score AS FLOAT) / NULLIF(total, 0)) * 100 AS avg FROM quiz_history"
        ).fetchone()["avg"]
        fc_count = conn.execute("SELECT COUNT(*) AS n FROM flashcards").fetchone()["n"]
    return {
        "topics_studied": topics_count or 0,
        "quizzes_taken": quiz_count or 0,
        "average_score": round(avg or 0, 1),
        "flashcards": fc_count or 0,
    }


def recent_activity(limit: int = 8):
    """Combine topics + quizzes into a unified recent feed."""
    with get_conn() as conn:
        rows = conn.execute(
            f"""
            SELECT 'Studied' AS kind, topic AS detail, studied_at AS ts
              FROM topics
            UNION ALL
            SELECT 'Quiz (' || difficulty || ')' AS kind,
                   topic || ' — ' || score || '/' || total AS detail,
                   taken_at AS ts
              FROM quiz_history
            ORDER BY ts DESC LIMIT {int(limit)}
            """
        ).fetchall()
    return [dict(r) for r in rows]


def low_score_topics(threshold: float = 60.0):
    """Return topics where average % score < threshold."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT topic,
                   AVG(CAST(score AS FLOAT) / NULLIF(total,0)) * 100 AS pct,
                   COUNT(*) AS attempts
              FROM quiz_history
             GROUP BY topic
            HAVING pct < ?
             ORDER BY pct ASC
            """,
            (threshold,),
        ).fetchall()
    return [dict(r) for r in rows]
