"""Simulated human-in-the-loop gate for side-effectful tools.

Lab design: when SECURE_MODE=true, email and file-write are denied unless
LAB_APPROVE=1 (or true/yes). This is intentionally non-interactive so attack
scripts and metrics stay automatable. Real HITL UI is out of scope for v1.0.
"""
from __future__ import annotations

import os

SIDE_EFFECT_TOOLS = frozenset({"email_tool"})
# file write is also side-effectful; read/list are not.
FILE_WRITE_OPS = frozenset({"write"})


class ApprovalDenied(PermissionError):
    pass


def _lab_approved() -> bool:
    return os.environ.get("LAB_APPROVE", "0").lower() in ("1", "true", "yes")


def require_approval(tool: str, args: dict | None) -> None:
    args = args or {}
    if _lab_approved():
        return

    if tool in SIDE_EFFECT_TOOLS:
        raise ApprovalDenied(
            f"tool '{tool}' requires human approval (set LAB_APPROVE=1 to simulate approve)"
        )

    if tool == "file_tool" and args.get("op") in FILE_WRITE_OPS:
        raise ApprovalDenied(
            "file_tool write requires human approval (set LAB_APPROVE=1 to simulate approve)"
        )
