"""Reconstructed AI & Agent Security curriculum (2026 IDs, Core track)."""
from __future__ import annotations

from guardrails.pipeline import find_sensitive, mask_sensitive, scan_data
from lab import content, credential, curriculum
from lab.sims_core import RUNNERS


def test_ai_area_has_core_persist_operate_tracks():
    scen = content.list_scenarios("ai-security")
    tracks = {s["id"]: s.get("track") for s in scen}
    core = [s for s in scen if s.get("track") == "core"]
    persist = [s for s in scen if s.get("track") == "persist"]
    operate = [s for s in scen if s.get("track") == "operate"]
    assert len(core) == 9, [s["id"] for s in core]
    reviewer = [s for s in scen if s.get("track") == "reviewer"]
    assert len(persist) == 5   # + 19-mcp-tool-poisoning (PLAN.md P5.3)
    assert len(operate) == 6
    assert len(reviewer) == 3  # read-only officials track (PLAN.md P5.4)
    assert tracks["16-direct-injection"] == "core"
    assert tracks["17-data-guards"] == "core"
    assert tracks["18-agent-identity"] == "core"
    assert content.get_area("ai-security")["credential"]["requires_track"] == "core"


def test_core_order_matches_reconstructed_syllabus():
    core = [s for s in content.list_scenarios("ai-security") if s.get("track") == "core"]
    assert [s["id"] for s in core] == [
        "00-orientation",
        "01-tool-abuse-sqli",
        "16-direct-injection",
        "02-rag-poisoning",
        "03-cross-tool-exfil",
        "17-data-guards",
        "18-agent-identity",
        "04-agent-exploit",
        "05-guardrail-map",
    ]


def test_badge_requires_core_only():
    required = credential.required_checks("ai-security")
    ids = {r["scenario"] for r in required}
    assert "17-data-guards" in ids
    assert "06-rag-deep-poisoning" not in ids
    assert "15-resource-limits" not in ids


def test_llm_2026_numbering():
    llm = curriculum.OWASP_LLM
    assert llm["LLM03"]["name"].startswith("Excessive Agency")
    assert llm["LLM06"]["name"].startswith("Unbounded Consumption")
    assert llm["LLM08"]["name"].startswith("Hidden Context")
    assert llm["LLM10"]["name"].startswith("Improper Output")
    asi = curriculum.OWASP_ASI
    assert asi["ASI04"]["name"].startswith("Agentic Supply Chain")
    assert asi["ASI05"]["covered"] is False
    assert set(asi) == {f"ASI{i:02d}" for i in range(1, 11)}
    assert "C21" in {c["id"] for c in curriculum.CONTROLS}


def test_new_core_runners_registered():
    for key in ("direct_pi", "data_guards", "agent_identity"):
        assert key in RUNNERS, key


def test_data_guard_detects_ssn_and_masks():
    hits = find_sensitive("ssn 078-05-1120 and alice@x.test")
    types = {h["type"] for h in hits}
    assert "ssn" in types and "email" in types
    assert "[SSN]" in mask_sensitive("078-05-1120")
    v = scan_data("078-05-1120", channel="input")
    assert v["action"] == "block"


def test_data_guard_sim_names_the_scanner():
    from defenses.config import secure_override
    from lab import events
    from lab.sims_core import sim_data_guards

    events.clear_events()
    with secure_override(True):
        result = sim_data_guards()
    assert result["blocked"] is True
    assert "pipeline.py" in (result.get("evidence") or {}).get("scanner", "")
    msgs = " ".join(e["message"] for e in events.list_events())
    assert "scan_data" in msgs
    assert "find_sensitive" in msgs
    assert "email_tool was never called" in msgs
    assert "078-05-1120" in msgs


def test_catalog_exposes_track():
    cat = content.catalog_payload()
    ai = next(a for a in cat["areas"] if a["id"] == "ai-security")
    tracks = {s["id"]: s.get("track") for s in ai["scenarios"]}
    assert tracks["17-data-guards"] == "core"
    assert tracks["11-supply-chain"] == "persist"
