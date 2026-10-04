"""Agent skills: why a pattern scanner misses a prose instruction, and what stops it.

A skill (``SKILL.md`` with YAML frontmatter, then prose) is loaded into the agent's
context. Its prose is read as instructions, so a sentence under "Usage notes" can tell
the agent to read a private file and mail it out. There is no code to scan.

Two things live here:

* ``scan_skill`` is the kind of scanner many registries run: a list of dangerous
  shell and code patterns. It is deliberately ordinary, and it passes the scenario 23
  skill as clean. That is the lesson (OWASP Agentic Skills Top 10 AST08, Poor Scanning).
* ``enforce`` is the control (C22): the skill's manifest declares the files and network
  it needs, and the runtime refuses anything undeclared, whatever the prose says
  (AISVS v1.0 C9.3.3 and C9.3.4).
"""
from __future__ import annotations

import re
from pathlib import Path

# The usual scanner list: shells, downloaders, encoders, dynamic execution.
SCAN_PATTERNS = {
    "shell download": r"\b(curl|wget)\b",
    "encoded payload": r"\bbase64\b",
    "dynamic execution": r"\b(eval|exec)\s*\(",
    "subprocess": r"\b(subprocess|os\.system|popen)\b",
    "reverse shell": r"/dev/tcp/|\bnc\s+-e\b",
    "pipe to shell": r"\|\s*(sh|bash)\b",
}


def parse_skill(text: str) -> tuple[dict, str]:
    """Split a SKILL.md into (frontmatter dict, prose). Small YAML subset, no dependency."""
    if not text.startswith("---"):
        return {}, text
    _, front, body = text.split("---", 2)
    meta: dict = {}
    perms: dict = {}
    in_perms = False
    for raw in front.strip().splitlines():
        if not raw.strip():
            continue
        if raw.startswith("permissions:"):
            in_perms = True
            continue
        key, _, value = raw.strip().partition(":")
        value = value.strip()
        parsed = [] if value == "[]" else [v.strip() for v in value.strip("[]").split(",") if v.strip()] if value.startswith("[") else value
        if in_perms and raw.startswith("  "):
            perms[key] = parsed
        else:
            in_perms = False
            meta[key] = parsed
    meta["permissions"] = perms
    return meta, body


def scan_skill(text: str) -> list[dict]:
    """Return pattern findings. An empty list means the scanner calls the skill clean."""
    findings = []
    for name, pattern in SCAN_PATTERNS.items():
        for m in re.finditer(pattern, text, re.IGNORECASE):
            findings.append({"rule": name, "match": m.group(0)})
    return findings


def enforce(meta: dict, action: dict) -> tuple[bool, str]:
    """(allowed, reason) for one action the skill's instructions lead to.

    ``action`` is ``{"kind": "file", "path": ...}`` or ``{"kind": "network", "to": ...}``.
    Anything not declared in ``permissions`` is refused.
    """
    perms = meta.get("permissions") or {}
    name = meta.get("name", "skill")
    if action["kind"] == "file":
        allowed = perms.get("files") or []
        if action["path"] in allowed:
            return True, f"'{name}' declares file access to {action['path']}"
        return False, (f"skill manifest: '{name}' declares files: {allowed or '[]'}; "
                       f"read of {action['path']} refused before it happened")
    if action["kind"] == "network":
        allowed = perms.get("network") or []
        if action["to"] in allowed:
            return True, f"'{name}' declares network access to {action['to']}"
        return False, f"skill manifest: '{name}' declares network: {allowed or '[]'}; send to {action['to']} refused"
    return False, f"unknown action kind {action['kind']!r}"


def load_skill(path: Path) -> tuple[dict, str, str]:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_skill(text)
    return meta, body, text
