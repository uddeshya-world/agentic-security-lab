"""Attack 1 Layer A: SQL injection filter + path traversal via tool HTTP.

Vuln mode: dumps all customers with filter=1=1; reads outside workspace via ../
Secure mode: both blocked by tool secure branches.
"""
from __future__ import annotations

import sys

from attacks.m01.common import (
    DB_TOOL_URL,
    FILE_TOOL_URL,
    AttackResult,
    exit_for_result,
    invoke_tool,
    tool_secure_mode,
)


def _outside_workspace(resolved: str) -> bool:
    norm = resolved.replace("\\", "/")
    return bool(resolved) and not norm.startswith("/workspace")


def run() -> AttackResult:
    secure = tool_secure_mode(DB_TOOL_URL)
    evidence: dict = {}

    sqli_ok = False
    try:
        data = invoke_tool(DB_TOOL_URL, {"table": "customers", "filter": "1=1"})
        evidence["sqli_response"] = data
        body = data.get("result") or {}
        if isinstance(body, dict) and not body.get("error"):
            count = int(body.get("count") or 0)
            rows = body.get("rows") or []
            sqli_ok = count >= 2 and len(rows) >= 2
        else:
            evidence["sqli_error"] = body.get("error") if isinstance(body, dict) else body
    except Exception as e:
        evidence["sqli_exception"] = str(e)

    trav_ok = False
    try:
        data = invoke_tool(FILE_TOOL_URL, {"op": "read", "path": "../etc/hostname"})
        evidence["traversal_response"] = data
        body = data.get("result") or {}
        if isinstance(body, dict) and body.get("error"):
            evidence["traversal_error"] = body["error"]
        elif isinstance(body, dict):
            content = body.get("content")
            resolved = str(body.get("resolved_path") or "")
            trav_ok = bool(content) and _outside_workspace(resolved)
    except Exception as e:
        evidence["traversal_exception"] = str(e)

    success = sqli_ok or trav_ok
    if secure:
        blocked = not success
        detail = (
            "Secure mode blocked param abuse"
            if blocked
            else "Secure mode FAILED to block param abuse"
        )
        detail += f" (sqli={sqli_ok}, path_traversal={trav_ok})"
    else:
        blocked = False
        detail = f"Parameter abuse: sqli={'yes' if sqli_ok else 'no'}, path_traversal={'yes' if trav_ok else 'no'}"

    return AttackResult(
        attack_id="a1_param_manipulation",
        name="Parameter manipulation (SQLi + path traversal)",
        layer="A",
        secure_mode=secure,
        success=success,
        blocked=blocked if secure else False,
        detail=detail,
        evidence=evidence,
    )


if __name__ == "__main__":
    try:
        exit_for_result(run())
    except Exception as e:
        print(f"Infrastructure error: {e}", file=sys.stderr)
        sys.exit(2)
