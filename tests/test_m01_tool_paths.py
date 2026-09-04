"""Offline tests for vuln vs secure tool logic (no Docker)."""
import sqlite3
from pathlib import Path

import pytest

from tools.db_tool import queries


def test_query_vulnerable_sqli(tmp_path, monkeypatch):
    db = tmp_path / "lab.db"
    monkeypatch.setattr(queries, "DB_PATH", db)
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE customers (customer_id INTEGER, name TEXT, email TEXT);
        INSERT INTO customers VALUES (1, 'Alice', 'a@example.test');
        INSERT INTO customers VALUES (2, 'Bob', 'b@example.test');
        """
    )
    conn.commit()
    conn.close()

    rows = queries.query_vulnerable("customers", "1=1")
    assert len(rows) == 2


def test_query_secure_scopes(tmp_path, monkeypatch):
    db = tmp_path / "lab.db"
    monkeypatch.setattr(queries, "DB_PATH", db)
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE customers (customer_id INTEGER, name TEXT, email TEXT);
        INSERT INTO customers VALUES (1, 'Alice', 'a@example.test');
        INSERT INTO customers VALUES (2, 'Bob', 'b@example.test');
        """
    )
    conn.commit()
    conn.close()

    rows = queries.query_secure("customers", 1)
    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"


def test_file_resolve_vuln_vs_secure(tmp_path):
    """Mirrors tools/file_tool/server.py resolve helpers without importing FastAPI app."""
    import os
    from pathlib import Path

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    canary = tmp_path / "secret.txt"
    canary.write_text("top-secret", encoding="utf-8")

    def resolve_vulnerable(path: str) -> Path:
        return Path(os.path.join(str(workspace), path))

    def resolve_secure(path: str) -> Path:
        candidate = (workspace / path).resolve()
        try:
            candidate.relative_to(workspace.resolve())
        except ValueError as e:
            raise PermissionError(f"path '{path}' escapes workspace jail") from e
        return candidate

    vuln = resolve_vulnerable("../secret.txt")
    assert vuln.resolve() == canary.resolve()
    assert vuln.read_text(encoding="utf-8") == "top-secret"

    with pytest.raises(PermissionError):
        resolve_secure("../secret.txt")
