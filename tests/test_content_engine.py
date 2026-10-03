"""Host-runnable tests for the lesson engine (no Docker required).

These guard the Phase 0 migration invariant — that folder content is the single
source of truth and the legacy lesson/exploit shapes survive — plus the Phase 1
per-request SECURE_MODE override contract.
"""
from __future__ import annotations

from defenses.config import get_override, is_secure, secure_override
from lab import content
from lab.checks import run_check
from lab.exploits import list_exploits
from lab.lessons import get_lesson, get_lessons


def test_catalog_loads_ai_security_area():
    cat = content.catalog_payload()
    assert cat["area_count"] >= 1
    ids = [a["id"] for a in cat["areas"]]
    assert "ai-security" in ids


def test_scenarios_are_ordered_and_unique():
    scen = content.list_scenarios("ai-security")
    orders = [s["order"] for s in scen]
    assert orders == sorted(orders), "scenarios must be ordered"
    assert len(orders) == len(set(orders)), "scenario order values must be unique"
    # Core (9) + persist (4) + operate (6) = 19 after the 2026 reconstruction.
    assert len(scen) >= 19


def test_legacy_lesson_ids_and_ordering_preserved():
    lessons = get_lessons()
    ids = [l["id"] for l in lessons]
    # Module 1 ids must keep their identity and order (simulate.py + console depend on them).
    assert ids[:6] == ["l0", "a1", "a2", "a3", "a4", "g1"]
    # Areas authored after the migration have no legacy id and must not appear here.
    assert all(i for i in ids), "a scenario without a legacy_id leaked into the legacy lesson list"
    # Modules 2-8 register their own lesson ids.
    for advanced in ("m2", "m3", "m4", "m5", "m6", "m7", "m8"):
        assert advanced in ids, f"missing advanced module lesson: {advanced}"
    # simulate.py hard-depends on these keys existing
    a4 = get_lesson("a4")
    assert a4 and a4["story"] and a4["takeaway"] and a4["attack_id"] == "a4_agent_exploit"
    assert a4["mailhog"] is True


def test_every_advanced_module_has_a_runner():
    """Each Modules 2-8 lesson must resolve to a registered deterministic sim."""
    from lab.simulate import RUNNERS

    for lesson_id in ("m2", "m3", "m4", "m5", "m6", "m7", "m8"):
        lesson = get_lesson(lesson_id)
        assert lesson is not None, f"no scenario for {lesson_id}"
        attack_id = lesson["attack_id"]
        assert attack_id in RUNNERS, f"{lesson_id} -> {attack_id} has no runner"


def test_exploit_shape_matches_legacy_contract():
    ex = list_exploits()
    assert [e["id"] for e in ex] == ["direct_sqli", "exfil_chain", "indirect_pi", "path_read"]
    first = ex[0]
    for key in ("id", "title", "prompt", "expected", "secure_expect", "owasp", "controls", "remediation"):
        assert key in first, f"missing legacy key: {key}"


def test_scenario_payload_has_steps_and_checks():
    sp = content.scenario_payload("ai-security", "01-tool-abuse-sqli")
    assert sp is not None
    assert len(sp["steps"]) == 6
    graded = [s for s in sp["steps"] if s["has_check"]]
    # Two attack/defend runs plus a recall question on the read-the-SQL step.
    assert len(graded) == 3
    assert {s["check_kind"] for s in graded} == {"evidence", "recall"}


def test_every_check_file_has_known_kind():
    known = {"evidence", "recall", "simulate", "mailhog", "lab_status", "secure_mode", "manual"}
    for scen in content.list_scenarios():
        for step in scen.get("steps") or []:
            chk = step.get("check")
            if chk:
                assert chk.get("kind") in known, f"{scen['id']}/{step['id']}: {chk.get('kind')}"


def test_secure_override_is_scoped_and_resets():
    assert get_override() is None
    base = is_secure()
    with secure_override(True):
        assert get_override() is True and is_secure() is True
    with secure_override(False):
        assert get_override() is False and is_secure() is False
    assert get_override() is None
    assert is_secure() == base


def test_manual_and_unknown_check_dispatch():
    assert run_check(None)["passed"] is True
    assert run_check({"kind": "manual"})["passed"] is True
    assert run_check({"kind": "does-not-exist"})["passed"] is False


def _graded_checks():
    """Yield (scenario_id, step_id, check) for every step that carries a check."""
    for scen in content.list_scenarios():
        for step in scen.get("steps") or []:
            chk = step.get("check")
            if chk:
                yield scen["id"], step["id"], chk


def test_every_graded_check_has_a_nonempty_asserts_array():
    missing = []
    for scen_id, step_id, chk in _graded_checks():
        asserts = chk.get("asserts")
        if not isinstance(asserts, list) or not (1 <= len(asserts) <= 4):
            missing.append((scen_id, step_id, chk.get("kind"), asserts))
    assert not missing, f"checks missing a 1-4 entry asserts array: {missing}"


def test_asserts_entries_are_short_and_well_formed():
    bad = []
    for scen_id, step_id, chk in _graded_checks():
        for entry in chk.get("asserts") or []:
            if len(entry) > 120:
                bad.append((scen_id, step_id, "too long", entry))
            elif entry.endswith("."):
                bad.append((scen_id, step_id, "trailing period", entry))
            elif not entry or not entry[0].islower():
                bad.append((scen_id, step_id, "not lowercase-start", entry))
    assert not bad, f"malformed asserts entries: {bad}"


def test_recall_client_payload_never_leaks_asserts_or_answer():
    for scen in content.list_scenarios():
        for step in scen.get("steps") or []:
            chk = step.get("check")
            if not chk or chk.get("kind") != "recall":
                continue
            client = content._client_check(step)
            assert client is not None
            assert "answer" not in client, f"{scen['id']}/{step['id']}: answer leaked to client"
            assert "asserts" not in client, f"{scen['id']}/{step['id']}: asserts leaked to client"


def test_non_recall_client_payload_carries_asserts():
    sp = content.scenario_payload("ai-security", "01-tool-abuse-sqli")
    assert sp is not None
    evidence_steps = [s for s in sp["steps"] if s.get("check_kind") == "evidence"]
    assert evidence_steps, "expected at least one evidence step in this scenario"
    for step in evidence_steps:
        assert step["check"] is not None
        assert step["check"].get("asserts"), f"{step['id']}: evidence step missing client-side asserts"
