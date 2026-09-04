"""Probe agent + tools + ollama for Lab Console status panel."""
from __future__ import annotations

import os
from typing import Any

import httpx

from defenses.config import is_secure


def _tool_urls() -> dict[str, str]:
    # Prefer in-compose service names when running inside the agent container.
    return {
        "db_tool": os.environ.get("DB_TOOL_URL")
        or os.environ.get("DB_TOOL_URL_HOST")
        or "http://127.0.0.1:8101",
        "email_tool": os.environ.get("EMAIL_TOOL_URL")
        or os.environ.get("EMAIL_TOOL_URL_HOST")
        or "http://127.0.0.1:8102",
        "file_tool": os.environ.get("FILE_TOOL_URL")
        or os.environ.get("FILE_TOOL_URL_HOST")
        or "http://127.0.0.1:8103",
    }


def _probe(url: str, path: str = "/health", timeout: float = 3.0) -> dict[str, Any]:
    try:
        r = httpx.get(f"{url}{path}", timeout=timeout)
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        return {"ok": r.status_code == 200, "status_code": r.status_code, "body": body}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def collect_status() -> dict[str, Any]:
    tools = {}
    for name, url in _tool_urls().items():
        probe = _probe(url)
        tools[name] = {
            "url": url,
            "ok": probe.get("ok", False),
            "secure_mode": (probe.get("body") or {}).get("secure_mode"),
            "error": probe.get("error"),
        }

    ollama_base = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
    ollama_model = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b-instruct")
    ollama = _probe(ollama_base, path="/api/tags", timeout=5.0)
    ollama_ok = ollama.get("ok", False)

    agent_secure = is_secure()
    tool_modes = [t.get("secure_mode") for t in tools.values() if t.get("ok")]
    all_secure = bool(tool_modes) and all(tool_modes) and agent_secure
    all_vuln = bool(tool_modes) and not any(tool_modes) and not agent_secure

    return {
        "agent": {
            "ok": True,
            "secure_mode": agent_secure,
            "lab_console": "/lab/ui/",
        },
        "tools": tools,
        "ollama": {
            "url": ollama_base,
            "model": ollama_model,
            "reachable_from_agent": ollama_ok,
            "note": (
                "Ollama is internal to Docker (not published to host by default). "
                "Module 1 simulations do NOT require Ollama; optional agent chat does."
            ),
        },
        "mailhog_ui": os.environ.get("MAILHOG_UI", "http://127.0.0.1:8025"),
        "mode_summary": {
            "agent_secure": agent_secure,
            "all_tools_secure": all_secure,
            "all_tools_vuln": all_vuln,
            "mixed": not all_secure and not all_vuln,
        },
        # Two different things get called "secure mode", and conflating them is the
        # most common student confusion in this lab. Return them as separate fields
        # rather than one blob with two shells mashed together, so the UI can show
        # the per-run switch first and the container recreate as the optional path.
        "secure_mode_help": {
            "per_run": (
                "Guided scenarios set the mode for one run with the switch above the timeline. "
                "Nothing rebuilds and nothing persists."
            ),
            "persistent": (
                "Recreating the containers hardens the long-running tool servers themselves, "
                "and it survives a reload."
            ),
            "bash": "SECURE_MODE=true docker compose up -d --force-recreate agent db-tool email-tool file-tool",
            "powershell": "$env:SECURE_MODE='true'; docker compose up -d --force-recreate agent db-tool email-tool file-tool",
            "revert": "Run the same command with SECURE_MODE=false to go back.",
        },
    }
