"""Guards for the first-student run fixes (PLAN.md fix batch F1).

A first full run of the Core path found the lessons drifting away from the UI
and the grader: stale "recreate the stack" instructions, "Check re-runs the
simulation", internal A1–A6 codes, quizzes answered by the paragraph above them,
and a capstone check that passed on any single guardrail. These tests keep those
from coming back. No Docker needed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from lab import credential, runlog
from lab.checks import run_check

ROOT = Path(__file__).resolve().parents[1]
SCEN = ROOT / "content" / "areas" / "ai-security" / "scenarios"
CORE = [
    "00-orientation", "01-tool-abuse-sqli", "16-direct-injection", "02-rag-poisoning",
    "03-cross-tool-exfil", "17-data-guards", "18-agent-identity", "04-agent-exploit",
    "05-guardrail-map",
]


def _core_text():
    for sid in CORE:
        for f in sorted((SCEN / sid).glob("*.md")):
            yield f"{sid}/{f.name}", f.read_text(encoding="utf-8")


def test_core_is_the_badge_path():
    for sid in CORE:
        meta = json.loads((SCEN / sid / "scenario.json").read_text(encoding="utf-8"))
        assert meta.get("track") == "core", sid


def test_lessons_never_say_check_runs_anything():
    bad = [rel for rel, t in _core_text() if re.search(r"\*\*Check\*\*\s+(re-?runs|runs the)", t)]
    assert not bad, bad


def test_lessons_use_scenario_names_not_internal_codes():
    pat = re.compile(r"\b(A[1-6]|G1)\b|Run simulation")
    bad = [f"{rel}: {m.group(0)}" for rel, t in _core_text() for m in pat.finditer(t)]
    assert not bad, bad


def test_recreating_the_stack_is_only_ever_optional():
    # Graded steps switch the mode per run. The one place that shows the recreate
    # command must label it optional.
    for rel, t in _core_text():
        if "--force-recreate" in t:
            assert "Optional" in t or "optional" in t, rel


def test_every_core_intro_has_an_analogy_and_where_it_breaks():
    for sid in CORE:
        intro = (SCEN / sid / "intro.md").read_text(encoding="utf-8")
        assert intro.startswith("> **In plain terms.**"), sid
        assert "*Where the analogy breaks:*" in intro, sid


def test_every_core_scenario_has_a_video_script():
    doc = (ROOT / "docs" / "video" / "CORE_VIDEO_SCRIPTS.md").read_text(encoding="utf-8")
    for sid in CORE:
        assert f"(`{sid}`" in doc, sid
    assert doc.count("Where the analogy breaks") >= len(CORE)
    assert "certified" not in doc.lower().replace("do not say \"certified\"", "")


def test_recall_answers_are_not_all_in_one_position():
    answers = []
    for sid in CORE:
        for f in (SCEN / sid / "checks").glob("*.json"):
            spec = json.loads(f.read_text(encoding="utf-8"))
            if spec.get("kind") == "recall":
                assert 0 <= spec["answer"] < len(spec["options"]), f
                answers.append(spec["answer"])
    assert len(set(answers)) >= 3, answers


def test_core_badge_still_needs_23_checks():
    assert len(credential.required_checks("ai-security")) == 23


# ---------------------------------------------------------------- grader


@pytest.fixture
def _clean_runlog():
    runlog.clear()
    yield
    runlog.clear()


def test_capstone_check_needs_all_three_guardrails(monkeypatch, _clean_runlog):
    spec = json.loads((SCEN / "04-agent-exploit" / "checks" / "step-05.json").read_text(encoding="utf-8"))
    assert len(spec["event_contains_all"]) == 3

    runlog.record("a4", secure=True, result={"success": False, "blocked": True, "attack_id": "a4"})
    one = [{"phase": "defense", "message": "GUARDRAIL L1 (retrieval trust filter): untrusted chunks filtered"}]
    monkeypatch.setattr("lab.events.list_events", lambda limit=500, since_id=0: one)
    assert run_check(spec)["passed"] is False

    three = one + [
        {"phase": "defense", "message": "GUARDRAIL blocked db_tool: db_tool requires customer_id"},
        {"phase": "defense", "message": "GUARDRAIL blocked email_tool: recipient domain not allow-listed"},
    ]
    monkeypatch.setattr("lab.events.list_events", lambda limit=500, since_id=0: three)
    assert run_check(spec)["passed"] is True


# ---------------------------------------------------------------- badge name


@pytest.mark.parametrize("raw, want", [
    (None, None),
    ("", None),
    ("   ", None),
    ("  Uddeshya   Kumar ", "Uddeshya Kumar"),
    ("A\x00li\x1b[31mce", "Ali[31mce"),
    ("x" * 200, "x" * credential.LEARNER_MAX),
    (42, None),
])
def test_badge_name_is_cleaned_and_capped(raw, want):
    assert credential.clean_learner(raw) == want


# ---------------------------------------------------------------- status hint


def test_status_names_the_network_when_every_tool_times_out(monkeypatch):
    from lab import status

    monkeypatch.setattr(status, "_probe", lambda url, path="/health", timeout=3.0: {"ok": False, "error": "timed out"})
    assert "cannot reach the other containers" in status.collect_status()["network_hint"]

    monkeypatch.setattr(status, "_probe", lambda url, path="/health", timeout=3.0: {"ok": True, "body": {}})
    assert status.collect_status()["network_hint"] is None


def test_terminal_tab_names_the_overlay_command_and_probes_first():
    # ttyd only exists in docker-compose.terminal.yml; "docker compose up -d ttyd" alone fails.
    html = (ROOT / "lab" / "ui" / "scenario.html").read_text(encoding="utf-8")
    assert "docker compose -f docker-compose.yml -f docker-compose.terminal.yml up -d ttyd" in html
    assert "<code>docker compose up -d ttyd</code>" not in html
    assert 'fetch(TTYD, { mode: "no-cors"' in html
