import httpx


def test_schema_reachable(email_tool_url):
    resp = httpx.get(f"{email_tool_url}/schema")
    resp.raise_for_status()
    assert resp.json()["name"] == "email_tool"


def test_send(email_tool_url, mailhog_api):
    resp = httpx.post(
        f"{email_tool_url}/invoke",
        json={"to": "test@example.test", "subject": "unit-test", "body": "body"},
    )
    resp.raise_for_status()
    assert resp.json()["result"]["sent"] is True
