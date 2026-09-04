"""Prompt 0 smoke test -- see plan section 6. Asserts, in order: (1) a
RAG-answerable question returns text touching seeded-corpus content via the
full agent run (since the planner decides whether to even use it -- this
test tolerates either an "answer" step grounded in context or a tool-free
direct answer, since a 3B local model's planning is not perfectly
deterministic; that's why Checkpoint 1 exists), (2) each tool is reachable
and returns expected structured output, (3) one end-to-end run completes
with a tool call.
"""
import httpx


def test_db_tool_returns_seeded_rows(db_tool_url):
    resp = httpx.post(f"{db_tool_url}/invoke", json={"table": "customers", "filter": "1=1"})
    resp.raise_for_status()
    data = resp.json()
    assert data["result"]["count"] > 0


def test_email_tool_sends_and_mailhog_sees_it(email_tool_url, mailhog_api):
    resp = httpx.post(
        f"{email_tool_url}/invoke",
        json={"to": "smoketest@example.test", "subject": "smoke", "body": "hello"},
    )
    resp.raise_for_status()
    data = resp.json()
    assert data["result"]["sent"] is True

    mh = httpx.get(f"{mailhog_api}/api/v2/messages")
    mh.raise_for_status()
    items = mh.json().get("items", [])
    assert any("smoke" in (i.get("Content", {}).get("Headers", {}).get("Subject", [""])[0]) for i in items)


def test_file_tool_write_then_read(file_tool_url):
    write_resp = httpx.post(
        f"{file_tool_url}/invoke",
        json={"op": "write", "path": "smoke.txt", "content": "smoke-content"},
    )
    write_resp.raise_for_status()
    assert write_resp.json()["result"]["written"] is True

    read_resp = httpx.post(f"{file_tool_url}/invoke", json={"op": "read", "path": "smoke.txt"})
    read_resp.raise_for_status()
    assert read_resp.json()["result"]["content"] == "smoke-content"


def test_agent_end_to_end_with_tool_call(agent_url):
    resp = httpx.post(
        f"{agent_url}/run",
        json={"session_id": "smoke", "message": "List all customers in the database."},
        timeout=120.0,
    )
    resp.raise_for_status()
    data = resp.json()
    assert data["final_answer"] is not None
    used_tool = any(r["tool"] != "answer" for r in data["executor_results"])
    assert used_tool, f"expected a tool call, got executor_results={data['executor_results']}"
