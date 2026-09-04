"""Runs INSIDE the agent container (in-process SQLite at /data/memory.db):
    docker compose exec agent pytest tests/test_memory.py -v
"""
from memory import store


def test_session_roundtrip():
    store.write_session("test-session", "k1", "v1")
    data = store.read_session("test-session")
    assert data["k1"] == "v1"


def test_long_term_roundtrip():
    store.write_long_term("test-session", "some final answer")
    entries = store.read_long_term("test-session")
    assert "some final answer" in entries
