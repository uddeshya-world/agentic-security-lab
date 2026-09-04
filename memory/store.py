"""SQLite-backed session + long-term memory. Writes are unvalidated and read
back into context verbatim -- intentional weakness, and the exact read/write
call sites module 4 (memory poisoning) will build on later without needing
to touch agents/graph.py.
"""
import datetime
import sqlite3
from pathlib import Path

DB_PATH = Path("/data/memory.db")


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    schema_path = Path(__file__).parent / "schema.sql"
    conn.executescript(schema_path.read_text())
    return conn


def write_session(session_id: str, key: str, value: str) -> None:
    conn = _connect()
    conn.execute(
        "INSERT INTO session_memory (session_id, key, value, updated_at) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(session_id, key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
        (session_id, key, value, datetime.datetime.now(datetime.timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def read_session(session_id: str) -> dict:
    conn = _connect()
    rows = conn.execute(
        "SELECT key, value FROM session_memory WHERE session_id = ?", (session_id,)
    ).fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}


def write_long_term(session_id: str, content: str) -> None:
    conn = _connect()
    conn.execute(
        "INSERT INTO long_term_memory (session_id, content, created_at) VALUES (?, ?, ?)",
        (session_id, content, datetime.datetime.now(datetime.timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def read_long_term(session_id: str, limit: int = 5) -> list[str]:
    conn = _connect()
    rows = conn.execute(
        "SELECT content FROM long_term_memory WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit),
    ).fetchall()
    conn.close()
    return [r["content"] for r in rows]
