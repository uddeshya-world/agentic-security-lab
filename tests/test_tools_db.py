import httpx


def test_schema_reachable(db_tool_url):
    resp = httpx.get(f"{db_tool_url}/schema")
    resp.raise_for_status()
    schema = resp.json()
    assert schema["name"] == "db_tool"


def test_query_orders(db_tool_url):
    resp = httpx.post(f"{db_tool_url}/invoke", json={"table": "orders", "filter": "1=1"})
    resp.raise_for_status()
    data = resp.json()
    assert data["result"]["count"] >= 4
