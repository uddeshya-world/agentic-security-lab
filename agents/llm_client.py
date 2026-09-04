"""Thin LLM abstraction. Ollama now; swappable to an API-key backend later by
adding a branch here -- callers (planner.py) never touch the backend
directly.
"""
import json
import os

import httpx

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b-instruct")


def chat(messages: list[dict], tools: list[dict] | None = None) -> dict:
    """Sends a chat request to Ollama. Returns the raw response message dict,
    which may include a 'tool_calls' key if the model invoked native
    tool-calling. Caller is responsible for falling back to parsing a fenced
    JSON block if 'tool_calls' is absent/malformed (see Checkpoint 1 finding,
    documented in FINDINGS-00.md).
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
    }
    if tools:
        payload["tools"] = tools

    # CPU hosts: 3B models often need several minutes cold; override via OLLAMA_TIMEOUT_S.
    timeout_s = float(os.environ.get("OLLAMA_TIMEOUT_S", "600"))
    resp = httpx.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=timeout_s)
    resp.raise_for_status()
    data = resp.json()
    return data.get("message", {})


def extract_json_block(text: str) -> dict | None:
    """Fallback parser: pulls the first fenced ```json ... ``` block (or the
    first {...} span) out of a text response. Used when native tool-calling
    JSON isn't reliable enough (see Checkpoint 1)."""
    if "```json" in text:
        start = text.index("```json") + len("```json")
        end = text.index("```", start)
        candidate = text[start:end].strip()
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        candidate = text[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None
