import httpx


def test_schema_reachable(file_tool_url):
    resp = httpx.get(f"{file_tool_url}/schema")
    resp.raise_for_status()
    assert resp.json()["name"] == "file_tool"


def test_write_list_read(file_tool_url):
    httpx.post(
        f"{file_tool_url}/invoke", json={"op": "write", "path": "unit.txt", "content": "x"}
    ).raise_for_status()

    list_resp = httpx.post(f"{file_tool_url}/invoke", json={"op": "list", "path": "."})
    list_resp.raise_for_status()
    assert "unit.txt" in list_resp.json()["result"]["entries"]

    read_resp = httpx.post(f"{file_tool_url}/invoke", json={"op": "read", "path": "unit.txt"})
    read_resp.raise_for_status()
    assert read_resp.json()["result"]["content"] == "x"
