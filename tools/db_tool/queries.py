"""Vulnerable-by-design and secure query paths for the db tool.

VULNERABLE_MODE (SECURE_MODE=false): the caller's `filter` string is
concatenated directly into the SQL WHERE clause -- classic SQL injection,
chosen deliberately (see plan section 0) over an "unscoped filter parameter"
as a more visceral, recognizable teaching demo. Do not parameterize this path;
that's the whole point until defenses/01/least_privilege.py is wired in.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("/data/synthetic_db/lab.db")

ALLOWED_TABLES = {"customers", "orders"}


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_seeded() -> None:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS customers ("
        "customer_id INTEGER PRIMARY KEY, name TEXT, email TEXT)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS orders ("
        "order_id INTEGER PRIMARY KEY, customer_id INTEGER, item TEXT, amount REAL)"
    )
    cur.execute("SELECT COUNT(*) FROM customers")
    if cur.fetchone()[0] == 0:
        seed_sql_path = Path("/data/synthetic_db/seed.sql")
        if seed_sql_path.exists():
            conn.executescript(seed_sql_path.read_text())
    conn.commit()
    conn.close()


def query_vulnerable(table: str, filter_fragment: str) -> list[dict]:
    """Raw SQL injection path. `table` is allow-listed to a fixed set of
    table names (so this isn't *also* a table-name-injection bug), but
    `filter_fragment` is concatenated into the WHERE clause verbatim.
    """
    if table not in ALLOWED_TABLES:
        raise ValueError(f"unknown table: {table}")
    conn = _connect()
    sql = f"SELECT * FROM {table} WHERE {filter_fragment}"  # nosec: intentional
    cur = conn.cursor()
    cur.execute(sql)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def query_secure(table: str, customer_id: int) -> list[dict]:
    """Parameterized, scope-enforced path used when SECURE_MODE=true."""
    if table not in ALLOWED_TABLES:
        raise ValueError(f"unknown table: {table}")
    conn = _connect()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE customer_id = ?", (customer_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
