"""Client-side tool registry: tool name -> base URL. The executor is the
only consumer of this module. Swapping the transport later (real MCP server
wrapping the same tool logic) only touches this file + tool entrypoints.
"""
import os

import httpx

TOOL_URLS = {
    "db_tool": os.environ.get("DB_TOOL_URL", "http://db-tool:8101"),
    "email_tool": os.environ.get("EMAIL_TOOL_URL", "http://email-tool:8102"),
    "file_tool": os.environ.get("FILE_TOOL_URL", "http://file-tool:8103"),
}


def _override_headers() -> dict:
    """Propagate the app's per-request SECURE_MODE override to tool servers.

    When the guided engine forces a mode for a graded check, the executor and
    the tool servers must agree. We send the decision as a header the tool
    server honors for that request only; outside an override no header is sent
    and the tool's own SECURE_MODE env stays authoritative.
    """
    from defenses.config import get_override

    ov = get_override()
    if ov is None:
        return {}
    return {"X-Secure-Mode": "true" if ov else "false"}


def get_schema(tool_name: str) -> dict:
    url = TOOL_URLS[tool_name]
    resp = httpx.get(f"{url}/schema", timeout=10.0)
    resp.raise_for_status()
    return resp.json()


def invoke(tool_name: str, args: dict) -> dict:
    url = TOOL_URLS[tool_name]
    resp = httpx.post(f"{url}/invoke", json=args, headers=_override_headers(), timeout=30.0)
    resp.raise_for_status()
    return resp.json()


def all_schemas() -> dict[str, dict]:
    return {name: get_schema(name) for name in TOOL_URLS}
