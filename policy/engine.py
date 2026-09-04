"""Module 8: policy-as-code engine + audit trail (real, in-process).

The ``policy/opa_seam.py`` stub always allows. This is the real evaluator a
governance module wires in. Rules are expressed as data (a small decision
matrix keyed on tool + blast radius), so they are auditable and testable like a
Rego bundle would be — without needing a network OPA sidecar in the lab.

Every evaluation appends to a queryable audit trail: who (agent), what
(tool+args), the decision, why (rule), and when.
"""
from __future__ import annotations

import datetime

# Blast radius per tool: how much damage a single call can do if wrong.
BLAST_RADIUS = {
    "answer": "none",
    "db_tool": "medium",     # reads data
    "file_tool": "high",     # writes state
    "email_tool": "critical",  # data leaves the boundary
}

# Decision matrix: blast radius -> default disposition.
MATRIX = {
    "none": "allow",
    "low": "allow",
    "medium": "allow",
    "high": "require_approval",
    "critical": "require_approval",
}

_AUDIT: list[dict] = []


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def evaluate(tool: str, args: dict, *, agent: str = "executor", approved: bool = False) -> dict:
    """Return {decision, reason, blast_radius}. Records an audit entry."""
    radius = BLAST_RADIUS.get(tool, "high")
    disposition = MATRIX.get(radius, "require_approval")

    # Extra rule: sending outside an owned domain is always denied, regardless.
    if tool == "email_tool":
        to = str(args.get("to", ""))
        if to and not to.endswith("@example.test"):
            decision, reason = "deny", f"egress to non-owned domain '{to}' is denied by policy"
            return _record(agent, tool, args, decision, reason, radius)

    if disposition == "require_approval":
        decision = "allow" if approved else "deny"
        reason = (
            f"{radius}-blast action approved by human (HITL)"
            if approved
            else f"{radius}-blast action requires human approval (default deny)"
        )
    else:
        decision, reason = "allow", f"{radius}-blast action auto-allowed by policy"
    return _record(agent, tool, args, decision, reason, radius)


def _record(agent, tool, args, decision, reason, radius) -> dict:
    entry = {
        "ts": _now(), "agent": agent, "tool": tool, "args": args,
        "decision": decision, "reason": reason, "blast_radius": radius,
    }
    _AUDIT.append(entry)
    return {"decision": decision, "reason": reason, "blast_radius": radius}


def audit_log(limit: int = 50) -> list[dict]:
    return _AUDIT[-limit:]


def audit_completeness(expected_actions: int) -> dict:
    """How many evaluated actions produced an audit entry (should be 100%)."""
    logged = len(_AUDIT)
    return {"expected": expected_actions, "logged": logged,
            "complete": logged >= expected_actions > 0}


def reset_audit() -> None:
    _AUDIT.clear()
