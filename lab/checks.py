"""Verification engine for guided scenario steps.

A step's check is a small declarative JSON spec (``content/.../checks/<step>.json``).
Checks assert real lab state, not just script exit codes — this is the platform's
differentiator over a generic terminal grader:

- ``evidence``   — assert against the run the student actually performed (see
                   ``lab.runlog``) plus the events it left behind. This is the
                   default for graded steps: **Run does the work, Check reads the
                   result.** A student who never pressed Run cannot pass.
- ``recall``     — a question about what just happened, graded server-side so the
                   answer never ships to the browser. Stops read-only scenarios
                   from being completable by pressing Next repeatedly.
- ``simulate``   — run a deterministic lab simulation in a forced mode and assert
                   the outcome (``success`` / ``blocked`` / ``ran``). Never depends
                   on the live LLM or its timeout/fallback path. Retained for steps
                   where running *is* the exercise (health checks, setup).
- ``mailhog``    — query the MailHog sink and assert a matching message is / isn't
                   present (did the exfil actually land / get stopped?).
- ``lab_status`` — assert the stack is healthy (all tool servers reachable).
- ``secure_mode``— assert the persistent container mode.
- ``manual``     — reading/acknowledgement step; always passes when invoked.

Every check returns the same shape so the stepper renders uniformly:
``{ok, passed, message, kind, evidence}``.
"""
from __future__ import annotations

import os
from typing import Any

import httpx

MAILHOG_API = os.environ.get("MAILHOG_API_BASE") or (
    "http://mailhog:8025"
    if os.environ.get("DB_TOOL_URL", "").startswith("http://db-tool")
    else "http://127.0.0.1:8025"
)


def _result(passed: bool, message: str, kind: str, evidence: Any = None) -> dict:
    return {"ok": True, "passed": bool(passed), "message": message, "kind": kind, "evidence": evidence}


def _mode_to_override(require_mode: str | None) -> bool | None:
    if require_mode in (None, "", "any"):
        return None
    return require_mode == "secure"


def _check_simulate(check: dict) -> dict:
    from lab.simulate import run_simulation

    sim_id = check.get("simulate")
    expect = check.get("expect", "success")
    override = _mode_to_override(check.get("require_mode"))

    run = run_simulation(sim_id, clear=True, secure=override)
    if not run.get("ok"):
        return _result(False, f"Simulation error: {run.get('error', 'unknown')}", "simulate", run)

    result = run.get("result") or {}
    events = run.get("events") or []
    success = bool(result.get("success"))
    blocked = bool(result.get("blocked"))

    # Optional stronger assertion: a guardrail event must actually have fired.
    if expect == "blocked" and check.get("require_event"):
        want = check["require_event"]
        if not any((e.get("phase") == want) for e in events):
            return _result(
                False,
                check.get("fail_message") or f"Expected a '{want}' event but none was recorded.",
                "simulate",
                {"result": result},
            )

    if expect == "success":
        passed = success
    elif expect == "blocked":
        passed = blocked
    elif expect == "ran":
        passed = bool(run.get("ok"))
    else:
        passed = success

    msg = (check.get("pass_message") if passed else check.get("fail_message")) or result.get("detail") or ""
    return _result(passed, msg, "simulate", {"detail": result.get("detail"), "attack_id": result.get("attack_id")})


def _check_evidence(check: dict, step_key: str | None = None) -> dict:
    """Grade the run the student performed, not a run this check kicks off itself."""
    from lab import events as event_store
    from lab import runlog

    sim_id = check.get("simulate")
    require_mode = check.get("require_mode")
    expect = check.get("expect", "success")

    ok, reason = runlog.matches(sim_id, require_mode, step_key=step_key)
    if not ok:
        return _result(False, reason, "evidence", {"run": runlog.last()})

    run = runlog.last() or {}
    recorded = event_store.list_events(limit=500)

    # Optional stronger assertions against the timeline the run actually wrote.
    want_phase = check.get("require_event")
    if want_phase and not any(e.get("phase") == want_phase for e in recorded):
        return _result(
            False,
            check.get("fail_message")
            or f"The run left no '{want_phase}' event. Read the timeline — the attack did not reach that stage.",
            "evidence",
            {"run": run},
        )

    needle = check.get("event_contains")
    if needle and not any(needle.lower() in (e.get("message") or "").lower() for e in recorded):
        return _result(
            False,
            check.get("fail_message") or f"Expected to find {needle!r} in the run's timeline, but it is not there.",
            "evidence",
            {"run": run},
        )

    if expect == "success":
        passed = run.get("success", False)
    elif expect == "blocked":
        passed = run.get("blocked", False)
    elif expect == "ran":
        passed = True
    else:
        passed = run.get("success", False)

    msg = (check.get("pass_message") if passed else check.get("fail_message")) or run.get("detail") or ""
    return _result(passed, msg, "evidence", {"run": run, "event_count": len(recorded)})


def _check_recall(check: dict, answer: Any = None) -> dict:
    """Grade a short question about what the student just saw.

    The correct answer lives only here — ``scenario_payload`` ships the prompt and
    the options, never the key. Otherwise the answer is one View-Source away.
    """
    options = check.get("options") or []
    correct = check.get("answer")

    if answer is None or answer == "":
        return _result(False, "Pick an answer, then check.", "recall", {"answered": False})

    if isinstance(correct, int):
        try:
            given = int(answer)
        except (TypeError, ValueError):
            return _result(False, "That is not one of the options.", "recall", {"answered": True})
        passed = given == correct
        chosen = options[given] if 0 <= given < len(options) else str(answer)
    else:
        passed = str(answer).strip().lower() == str(correct).strip().lower()
        chosen = str(answer)

    if passed:
        msg = check.get("pass_message") or "Correct."
    else:
        msg = check.get("fail_message") or "Not quite — re-read the step and the timeline, then try again."
    return _result(passed, msg, "recall", {"chosen": chosen, "answered": True})


def _check_mailhog(check: dict) -> dict:
    to_contains = check.get("to_contains")
    subject_contains = check.get("subject_contains")
    expect_present = check.get("expect_present", True)
    try:
        resp = httpx.get(f"{MAILHOG_API}/api/v2/messages", timeout=10.0)
        resp.raise_for_status()
        items = resp.json().get("items") or []
    except Exception as e:  # noqa: BLE001
        return _result(False, f"Could not reach MailHog: {e}", "mailhog")

    found = False
    for item in items:
        headers = item.get("Content", {}).get("Headers", {})
        subjects = " ".join(headers.get("Subject") or [])
        tos = " ".join(headers.get("To") or [])
        if to_contains and to_contains not in tos:
            continue
        if subject_contains and subject_contains not in subjects:
            continue
        found = True
        break

    passed = found == bool(expect_present)
    msg = (check.get("pass_message") if passed else check.get("fail_message")) or (
        f"Matching message {'found' if found else 'not found'} in MailHog."
    )
    return _result(passed, msg, "mailhog", {"message_count": len(items), "found": found})


def _check_lab_status(check: dict) -> dict:
    from lab.status import collect_status

    status = collect_status()
    tools = status.get("tools") or {}
    all_ok = bool(tools) and all(t.get("ok") for t in tools.values())
    passed = all_ok
    msg = (check.get("pass_message") if passed else check.get("fail_message")) or (
        "All tool servers healthy." if passed else "One or more tool servers are not responding."
    )
    return _result(passed, msg, "lab_status", {"tools": tools})


def _check_secure_mode(check: dict) -> dict:
    from defenses.config import is_secure

    want = bool(check.get("expect", True))
    actual = is_secure()
    passed = actual == want
    msg = (check.get("pass_message") if passed else check.get("fail_message")) or (
        f"SECURE_MODE is {'on' if actual else 'off'}."
    )
    return _result(passed, msg, "secure_mode", {"secure_mode": actual})


def run_check(check: dict | None, answer: Any = None, step_key: str | None = None) -> dict:
    if not check:
        return _result(True, "No verification for this step — mark it read to continue.", "manual")
    kind = (check.get("kind") or "manual").lower()
    if kind == "recall":
        try:
            return _check_recall(check, answer)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "passed": False, "message": f"Check errored: {e}", "kind": kind, "evidence": None}
    if kind == "evidence":
        try:
            return _check_evidence(check, step_key=step_key)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "passed": False, "message": f"Check errored: {e}", "kind": kind, "evidence": None}
    dispatch = {
        "simulate": _check_simulate,
        "mailhog": _check_mailhog,
        "lab_status": _check_lab_status,
        "secure_mode": _check_secure_mode,
        "manual": lambda c: _result(True, c.get("pass_message") or "Step acknowledged.", "manual"),
    }
    fn = dispatch.get(kind)
    if fn is None:
        return _result(False, f"Unknown check kind: {kind}", kind)
    try:
        return fn(check)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "passed": False, "message": f"Check errored: {e}", "kind": kind, "evidence": None}
