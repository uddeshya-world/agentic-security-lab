"""The Run/Check split, the recall answer key, and the credential gate.

These three properties are the ones a well-meaning refactor breaks quietly:

1. A Check that grades without a Run turns the button into a skip button, which
   is what an independent review of this lab found students doing.
2. A recall answer that ships to the browser is one View-Source away.
3. A badge issued before every graded check passed makes the badge worthless.

None of these fail loudly on their own, so they are asserted here.
"""
from __future__ import annotations

import pytest

from lab import content, credential, runlog
from lab.checks import run_check


@pytest.fixture(autouse=True)
def _clean_runlog():
    runlog.clear()
    yield
    runlog.clear()


# --------------------------------------------------------------------------
# 1. Check reads evidence; it never produces it.
# --------------------------------------------------------------------------

EVIDENCE_CHECK = {
    "kind": "evidence",
    "simulate": "a1",
    "require_mode": "vulnerable",
    "expect": "success",
}


def test_evidence_check_fails_when_nothing_has_been_run():
    result = run_check(EVIDENCE_CHECK)
    assert result["passed"] is False
    assert "run" in result["message"].lower()


def test_evidence_check_passes_only_after_a_matching_run():
    runlog.record("a1", secure=False, result={"success": True, "blocked": False, "attack_id": "a1"})
    assert run_check(EVIDENCE_CHECK)["passed"] is True


def test_evidence_check_rejects_a_run_in_the_wrong_mode():
    runlog.record("a1", secure=True, result={"success": False, "blocked": True, "attack_id": "a1"})
    result = run_check(EVIDENCE_CHECK)
    assert result["passed"] is False
    assert "secure" in result["message"] and "vulnerable" in result["message"]


def test_a_run_for_one_step_does_not_grade_another():
    """Two steps can drive the same sim in the same mode; a run belongs to one."""
    runlog.record(
        "a3", secure=False,
        result={"success": True, "blocked": False, "attack_id": "a3"},
        step_key="ai-security/03-cross-tool-exfil/step-02",
    )
    check = {"kind": "evidence", "simulate": "a3", "require_mode": "vulnerable", "expect": "success"}

    borrowed = run_check(check, step_key="blue-team/01-triage-the-exfil/step-02")
    assert borrowed["passed"] is False
    assert "different step" in borrowed["message"]

    owned = run_check(check, step_key="ai-security/03-cross-tool-exfil/step-02")
    assert owned["passed"] is True


def test_a_run_made_straight_against_the_api_still_counts():
    """Doing the work by hand is doing the work; only a *mismatched* step fails."""
    runlog.record("a1", secure=False, result={"success": True, "blocked": False, "attack_id": "a1"})
    assert run_check(EVIDENCE_CHECK, step_key="ai-security/01-tool-abuse-sqli/step-02")["passed"] is True


def test_evidence_check_rejects_a_run_of_a_different_attack():
    runlog.record("a3", secure=False, result={"success": True, "blocked": False, "attack_id": "a3"})
    result = run_check(EVIDENCE_CHECK)
    assert result["passed"] is False
    assert "a1" in result["message"]


def test_every_graded_step_is_gated_on_a_run_or_on_real_state():
    """No graded step may use a kind that performs the exercise for the student."""
    offenders = []
    for area in content.list_areas():
        for scen in area.get("scenarios") or []:
            for step in scen.get("steps") or []:
                check = step.get("check")
                if check and (check.get("kind") or "").lower() == "simulate":
                    offenders.append(f"{area['id']}/{scen['id']}/{step['id']}")
    assert not offenders, (
        "these checks run the attack themselves instead of grading the student's run: " + ", ".join(offenders)
    )


# --------------------------------------------------------------------------
# 2. The recall answer key stays on the server.
# --------------------------------------------------------------------------

RECALL_CHECK = {
    "kind": "recall",
    "prompt": "Which statement reached the database?",
    "options": ["SELECT ... WHERE customer_id = ?", "SELECT * FROM customers WHERE 1=1"],
    "answer": 1,
}


def test_recall_grades_server_side():
    assert run_check(RECALL_CHECK, answer=1)["passed"] is True
    assert run_check(RECALL_CHECK, answer=0)["passed"] is False


def test_recall_requires_an_answer():
    result = run_check(RECALL_CHECK, answer=None)
    assert result["passed"] is False
    assert "pick" in result["message"].lower()


def test_recall_answer_key_never_reaches_the_client():
    for area in content.list_areas():
        for scen in area.get("scenarios") or []:
            payload = content.scenario_payload(area["id"], scen["id"])
            for step in payload["steps"]:
                client_check = step.get("check") or {}
                assert "answer" not in client_check, f"{scen['id']}/{step['id']} leaks its answer key"


def test_recall_questions_offer_real_choices():
    for area in content.list_areas():
        for scen in area.get("scenarios") or []:
            for step in scen.get("steps") or []:
                check = step.get("check") or {}
                if (check.get("kind") or "") != "recall":
                    continue
                options = check.get("options") or []
                assert len(options) >= 3, f"{scen['id']}/{step['id']} has too few options to be a real question"
                assert isinstance(check.get("answer"), int)
                assert 0 <= check["answer"] < len(options)


# --------------------------------------------------------------------------
# 3. The badge is gated on every graded check, and is tamper-evident.
# --------------------------------------------------------------------------


def test_badge_is_refused_until_every_graded_check_passes():
    result = credential.issue("ai-security", learner=None, passed=[])
    assert result["ok"] is False
    assert result["eligibility"]["eligible"] is False
    assert result["eligibility"]["required_count"] > 0


@pytest.fixture()
def _fresh_ledger(tmp_path, monkeypatch):
    """The badge is minted from the server ledger, so seed a throwaway one."""
    from lab import ledger
    monkeypatch.setattr(ledger, "PATH", tmp_path / "ledger.json")
    monkeypatch.setattr(ledger, "_data", {"passes": {}})
    return ledger


def _record_all(ledger, required):
    for r in required:
        ledger.record_pass("ai-security", r["scenario"], r["step"], r["kind"], r["mode"])


def test_badge_issues_with_a_full_transcript_and_verifies(_fresh_ledger):
    required = credential.required_checks("ai-security")
    _record_all(_fresh_ledger, required)
    issued = credential.issue("ai-security", learner="tester", passed=[])
    assert issued["ok"] is True
    assert len(issued["assertion"]["evidence"]["transcript"]) == len(required)

    verified = credential.verify_token(issued["token"])
    assert verified["valid"] is True


def test_an_edited_badge_fails_verification(_fresh_ledger):
    required = credential.required_checks("ai-security")
    _record_all(_fresh_ledger, required)
    issued = credential.issue("ai-security", learner="tester", passed=[])

    tampered = dict(issued["assertion"])
    tampered["recipient"] = {"type": "identity", "hashed": False, "identity": "someone else"}
    forged = credential._encode_token(tampered, issued["signature"])

    assert credential.verify_token(forged)["valid"] is False


# --------------------------------------------------------------------------
# 4. Areas under construction never present themselves as live.
# --------------------------------------------------------------------------


def test_only_areas_meeting_the_live_bar_are_marked_available():
    payload = content.catalog_payload()
    for area in payload["areas"]:
        if area["status"] != "available":
            continue
        # A live Area needs an orientation plus graded attack/defend work.
        graded = sum(s["graded_steps"] for s in area["scenarios"])
        assert area["scenario_count"] >= 3, f"{area['id']} is marked available with too few scenarios"
        assert graded >= 4, f"{area['id']} is marked available with only {graded} graded checks"
