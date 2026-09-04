"""Record of the most recent graded run, so Check can read evidence instead of producing it.

The pedagogical rule this module exists to enforce: **Run does the work, Check
reads the result.** Before this split the Check button ran the attack *and*
graded it, which meant a student could complete every scenario without ever
looking at a SQL statement or an intercepted email.

Now the stepper calls ``POST /lab/simulate/...`` (Run), which records what
happened here, and ``POST /scenario/.../check/...`` (Check) asserts against this
record plus real lab state (MailHog, tool health). No run, no pass.

Single-process, in-memory, single-user — this is a local lab, not a multi-tenant
service. A restart clears it, which is correct: the event log is cleared on
restart too, so the evidence really is gone.
"""
from __future__ import annotations

import threading
import time
from typing import Any

_lock = threading.Lock()
_last: dict[str, Any] | None = None

# How long a run stays valid as evidence for a Check (seconds). Long enough to
# read the timeline and think; short enough that yesterday's run can't grade today.
MAX_AGE_SECONDS = 60 * 60


def record(
    sim_id: str,
    secure: bool,
    result: dict[str, Any],
    event_count: int = 0,
    step_key: str | None = None,
) -> None:
    """Called by the simulate route after every run.

    ``step_key`` is ``"<area>/<scenario>/<step>"`` when the run came from a
    step's Run button. Without it, a run of the right simulation in the right
    mode would satisfy *any* step that grades that pair — including a step in a
    different Area the learner never opened.
    """
    global _last
    with _lock:
        _last = {
            "sim_id": sim_id,
            "step_key": step_key,
            "attack_id": result.get("attack_id"),
            "secure": bool(secure),
            "mode": "secure" if secure else "vulnerable",
            "success": bool(result.get("success")),
            "blocked": bool(result.get("blocked")),
            "detail": result.get("detail"),
            "event_count": event_count,
            "at": time.time(),
        }


def last() -> dict[str, Any] | None:
    with _lock:
        if not _last:
            return None
        if time.time() - _last["at"] > MAX_AGE_SECONDS:
            return None
        return dict(_last)


def clear() -> None:
    global _last
    with _lock:
        _last = None


def matches(
    sim_id: str | None,
    require_mode: str | None,
    step_key: str | None = None,
) -> tuple[bool, str]:
    """Is the recorded run the one this step asked for?

    Returns ``(ok, reason)`` where ``reason`` is written for a student, not a log.
    """
    run = last()
    if not run:
        return False, "Nothing has been run yet. Use Run on this step first — Check reads the evidence, it doesn't produce it."

    # A run performed for one step never grades another, even when both drive
    # the same simulation in the same mode. Runs made straight against the API
    # carry no step, and those still count — doing the work by hand is doing the
    # work.
    recorded_step = run.get("step_key")
    if step_key and recorded_step and recorded_step != step_key:
        return False, (
            "The last run belongs to a different step. Press Run on this step, "
            "then check again."
        )

    if sim_id and run["sim_id"] != sim_id and run["attack_id"] != sim_id:
        return False, (
            f"The last run was '{run['sim_id']}', but this step grades '{sim_id}'. "
            "Run this step's attack, then check again."
        )

    if require_mode in (None, "", "any"):
        return True, ""

    want_secure = require_mode == "secure"
    if run["secure"] != want_secure:
        return False, (
            f"The last run was in {run['mode']} mode; this step grades the {require_mode} run. "
            f"Switch the run mode to {require_mode} and run it again."
        )
    return True, ""
