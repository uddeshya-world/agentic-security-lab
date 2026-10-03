"""Scenario 19 (MCP tool-description poisoning) and the reviewer track.

No Docker: the manifest pin is pure Python, and the content checks read the tree.
"""
from __future__ import annotations

import json
from pathlib import Path

from defenses.m07 import attestation
from defenses.m07.manifest_pin import (
    POISONED_WARD_LOOKUP,
    REVIEWED_WARD_LOOKUP,
    manifest_hash,
    review_gate,
)

SCEN = Path(__file__).resolve().parents[1] / "content" / "areas" / "ai-security" / "scenarios"


def test_reviewed_manifest_is_admitted():
    ok, reason = review_gate(REVIEWED_WARD_LOOKUP)
    assert ok, reason


def test_changed_description_is_held_for_review():
    ok, reason = review_gate(POISONED_WARD_LOOKUP)
    assert not ok
    assert "not pinned" in reason


def test_only_the_description_changed_so_capability_checks_alone_miss_it():
    """The lesson: publisher-and-capability attestation passes this update."""
    same = {k: v for k, v in POISONED_WARD_LOOKUP.items() if k not in ("description", "version")}
    base = {k: v for k, v in REVIEWED_WARD_LOOKUP.items() if k not in ("description", "version")}
    assert same == base
    assert manifest_hash(POISONED_WARD_LOOKUP) != manifest_hash(REVIEWED_WARD_LOOKUP)
    assert "send_email" in POISONED_WARD_LOOKUP["description"]
    assert POISONED_WARD_LOOKUP["description"].count(".example") == 1


def test_unknown_tool_is_refused():
    ok, _ = review_gate({**REVIEWED_WARD_LOOKUP, "name": "brand_new_tool"})
    assert not ok


def test_scenario_19_is_wired_to_its_simulation_both_ways():
    d = SCEN / "19-mcp-tool-poisoning"
    meta = json.loads((d / "scenario.json").read_text(encoding="utf-8"))
    assert meta["track"] == "persist"
    assert meta["legs"] == ["u", "p", "e"]
    assert any(o.startswith("ASI04") for o in meta["owasp"])
    assert any(o.startswith("LLM04:2026") for o in meta["owasp"])
    v = json.loads((d / "checks" / "step-02.json").read_text(encoding="utf-8"))
    s = json.loads((d / "checks" / "step-03.json").read_text(encoding="utf-8"))
    assert (v["simulate"], v["require_mode"], v["expect"]) == ("mcp_tool_poisoning", "vulnerable", "success")
    assert (s["simulate"], s["require_mode"], s["expect"]) == ("mcp_tool_poisoning", "secure", "blocked")


def test_scenario_19_runner_is_registered():
    src = (Path(__file__).resolve().parents[1] / "lab" / "sims_core.py").read_text(encoding="utf-8")
    assert '("mcp_tool_poisoning", sim_mcp_tool_poisoning)' in src


def test_reviewer_track_is_read_only_and_recall_only():
    found = []
    for meta_path in SCEN.glob("*/scenario.json"):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("track") != "reviewer":
            continue
        found.append(meta["id"])
        for chk in (meta_path.parent / "checks").glob("*.json"):
            spec = json.loads(chk.read_text(encoding="utf-8"))
            assert spec["kind"] == "recall", f"{meta['id']}/{chk.name} must be recall (no Docker)"
            assert "simulate" not in spec
    assert len(found) == 3, found


def test_attestation_still_refuses_unmanifested_tools():
    """The new pin extends C10/C15; it does not replace attestation."""
    ok, _ = attestation.attest("ward_lookup", None)
    assert not ok
