"""Module 3 defense: authenticated inter-agent messages + agent allow-list.

In the vulnerable multi-agent graph, one agent trusts another's output verbatim:
a plan passed from planner to executor is unsigned, so anything that can modify
it in transit (a compromised middle agent, a tampering step) is executed. And a
plan may name a tool/agent that was never registered.

The controls here are deliberately simple and real:
- ``sign`` / ``verify`` — HMAC over the canonical message with a shared lab key,
  so tampering is detected before execution.
- ``registry_allows`` — an explicit allow-list of agents/tools; anything else is
  rejected (no rogue-agent spawning).
"""
from __future__ import annotations

import hashlib
import hmac
import json

# Lab-only shared secret. In production each agent has its own key / mTLS identity.
_LAB_KEY = b"agentic-security-lab-m03-shared-key"

ALLOWED_AGENTS = {"planner", "executor", "reviewer"}
ALLOWED_TOOLS = {"db_tool", "email_tool", "file_tool", "answer"}


def _canonical(message: dict) -> bytes:
    return json.dumps(message, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign(message: dict) -> str:
    return hmac.new(_LAB_KEY, _canonical(message), hashlib.sha256).hexdigest()


def verify(message: dict, signature: str) -> bool:
    expected = sign(message)
    return hmac.compare_digest(expected, signature or "")


def registry_allows(*, agent: str | None = None, tool: str | None = None) -> bool:
    if agent is not None and agent not in ALLOWED_AGENTS:
        return False
    if tool is not None and tool not in ALLOWED_TOOLS:
        return False
    return True
