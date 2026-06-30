"""SQLite database for storing interview sessions and results."""

import json
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent.parent / "interviews.db"

# China timezone
CST = timezone(timedelta(hours=8))


def _now() -> str:
    return datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            resume_text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            question TEXT NOT NULL,
            reference_answer TEXT,
            difficulty TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            user_answer TEXT NOT NULL,
            score INTEGER,
            feedback TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL UNIQUE,
            overall_score INTEGER,
            strengths TEXT,
            weaknesses TEXT,
            recommendations TEXT,
            role_fit TEXT,
            full_report TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.commit()
    conn.close()


def create_session(role: str, difficulty: str, resume_text: str) -> int:
    """Create a new interview session, return session_id."""
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO sessions (role, difficulty, resume_text, created_at) VALUES (?, ?, ?, ?)",
        (role, difficulty, resume_text, _now()),
    )
    conn.commit()
    session_id = cur.lastrowid
    conn.close()
    return session_id


def save_questions(session_id: int, questions: list[dict]) -> None:
    """Save generated questions for a session."""
    conn = get_conn()
    for i, q in enumerate(questions, 1):
        conn.execute(
            "INSERT INTO questions (session_id, question_number, question, reference_answer, difficulty, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (
                session_id,
                i,
                q.get("question", ""),
                q.get("reference_answer", ""),
                q.get("difficulty", "medium"),
                _now(),
            ),
        )
    conn.commit()
    conn.close()


def save_answer(session_id: int, question_id: int, user_answer: str) -> int:
    """Save user's answer, return answer_id."""
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO answers (session_id, question_id, user_answer, created_at) VALUES (?, ?, ?, ?)",
        (session_id, question_id, user_answer, _now()),
    )
    conn.commit()
    answer_id = cur.lastrowid
    conn.close()
    return answer_id


def update_evaluation(answer_id: int, score: int, feedback: str) -> None:
    """Update answer with evaluation results."""
    conn = get_conn()
    conn.execute(
        "UPDATE answers SET score = ?, feedback = ? WHERE id = ?",
        (score, feedback, answer_id),
    )
    conn.commit()
    conn.close()


def save_report(
    session_id: int,
    overall_score: int,
    strengths: str,
    weaknesses: str,
    recommendations: str,
    role_fit: str,
    full_report: str,
) -> None:
    """Save final evaluation report."""
    conn = get_conn()
    conn.execute(
        "INSERT INTO reports (session_id, overall_score, strengths, weaknesses, recommendations, role_fit, full_report, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (session_id, overall_score, strengths, weaknesses, recommendations, role_fit, full_report, _now()),
    )
    conn.commit()
    conn.close()


def get_session_stats() -> dict[str, Any]:
    """Get overall usage statistics."""
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    total_answers = conn.execute("SELECT COUNT(*) FROM answers").fetchone()[0]
    avg_score = conn.execute("SELECT AVG(overall_score) FROM reports WHERE overall_score > 0").fetchone()[0]
    conn.close()
    return {
        "total_sessions": total,
        "total_answers": total_answers,
        "avg_score": round(avg_score, 1) if avg_score else 0,
    }


def get_recent_sessions(limit: int = 10) -> list[dict]:
    """Get recent interview sessions with basic info."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT s.id, s.role, s.difficulty, s.created_at, r.overall_score "
        "FROM sessions s LEFT JOIN reports r ON s.id = r.session_id "
        "ORDER BY s.created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Initialize DB on import
init_db()
