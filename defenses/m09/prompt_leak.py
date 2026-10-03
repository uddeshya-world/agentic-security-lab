"""LLM08 defense: system-prompt leakage detection (Hidden Context Exposure).

An agent's system prompt is not a secret and is not a security boundary — but it
is still reconnaissance. Leaking it hands an attacker the exact tool names, the
argument shapes, and the rules to talk around. In this lab the planner prompt
literally documents `db_tool ... "filter": "<SQL WHERE fragment>"` with a
dump-all example, so a leak is a printed exploit recipe.

Two controls:
- ``scan_for_leak`` — output-side detection: flag a response that reproduces
  distinctive spans of the system prompt (n-gram overlap, so paraphrase-resistant
  in the way a naive substring check is not).
- ``redact`` — replace the leaked span rather than returning it.

The deeper lesson the scenario teaches: **never put anything in the system prompt
you would not publish.** Detection is damage control, not the fix.
"""
from __future__ import annotations

import re
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parents[2] / "agents" / "prompts"

# Distinctive markers of this lab's planner prompt. Short, high-signal phrases
# that would not appear in a normal customer-facing answer.
CANARY_PHRASES = (
    "you are the planner in a multi-tool agent system",
    "respond with only a json object",
    "sql where fragment",
    "example dump-all",
    "tool rules:",
)


def _norm(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _ngrams(tokens: list[str], n: int = 6) -> set[str]:
    return {" ".join(tokens[i:i + n]) for i in range(max(0, len(tokens) - n + 1))}


def load_system_prompt(name: str = "planner_system.txt") -> str:
    path = PROMPT_DIR / name
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def scan_for_leak(response: str, system_prompt: str | None = None, *, threshold: int = 2) -> dict:
    """Detect system-prompt disclosure in an outbound response.

    Returns {leaked, reasons, overlap_ngrams}. ``threshold`` is the number of
    shared 6-grams that constitutes a leak (1 can be coincidence; 2+ is copying).
    """
    system_prompt = system_prompt if system_prompt is not None else load_system_prompt()
    reasons: list[str] = []

    low = (response or "").lower()
    hits = [p for p in CANARY_PHRASES if p in low]
    if hits:
        reasons.append(f"system-prompt canary phrase(s) present: {hits[:2]}")

    shared = _ngrams(_norm(response)) & _ngrams(_norm(system_prompt))
    if len(shared) >= threshold:
        reasons.append(f"{len(shared)} verbatim 6-gram spans shared with the system prompt")

    return {"leaked": bool(reasons), "reasons": reasons, "overlap_ngrams": len(shared)}


def redact(response: str, system_prompt: str | None = None) -> str:
    """Fail closed: replace a leaking response instead of returning it."""
    verdict = scan_for_leak(response, system_prompt)
    if not verdict["leaked"]:
        return response
    return "[response withheld: it disclosed internal system instructions]"
