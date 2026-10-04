"""Pin the AISVS v1.0 / Agentic Skills Top 10 registry and keep every citation earned.

Three properties (PLAN.md Phase 8):

1. The registry matches the published standards: 12 AISVS chapters, AST01–AST10, ids
   well formed and version-pinned.
2. **Earned mappings only.** A control may say it *demonstrates* an AISVS requirement
   only if ``proven_by`` names a graded, non-recall, secure-mode check in a scenario
   that lists that control. Recall checks prove knowledge, not lab state.
3. Lab controls are also numbered C1–C22, so outside the registry files every dotted
   AISVS id must be written ``AISVS v1.0 C9.2.1`` and must exist in the registry.

No Docker needed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from lab import curriculum, standards

ROOT = Path(__file__).resolve().parents[1]
SCEN = ROOT / "content" / "areas"

CHAPTERS = {
    "C1": "Training Data Integrity & Traceability",
    "C2": "Input Validation",
    "C3": "Model Lifecycle Management & Change Control",
    "C4": "Infrastructure, Configuration & Deployment Security",
    "C5": "Access Control & Identity for AI Components & Users",
    "C6": "Supply Chain Security for Models",
    "C7": "Model Behavior, Output Control & Safety Assurance",
    "C8": "Memory, Embeddings & Vector Database Security",
    "C9": "Orchestration & Agentic Security",
    "C10": "Model Context Protocol (MCP) Security",
    "C11": "Adversarial Robustness",
    "C12": "Monitoring, Logging & Anomaly Detection",
}
AST_NAMES = {
    "AST01": "Malicious Skills", "AST02": "Supply Chain Compromise", "AST03": "Over-Privileged Skills",
    "AST04": "Insecure Metadata", "AST05": "Untrusted External Instructions", "AST06": "Weak Isolation",
    "AST07": "Update Drift", "AST08": "Poor Scanning", "AST09": "No Governance", "AST10": "Cross-Platform Reuse",
}
REQ_ID = re.compile(r"^C(\d{1,2})\.(\d{1,2})\.(\d{1,2})$")


def _scenario(sid: str) -> tuple[dict, Path] | None:
    for meta in SCEN.glob(f"*/scenarios/{sid}/scenario.json"):
        return json.loads(meta.read_text(encoding="utf-8")), meta.parent
    return None


def _area_status(scen_dir: Path) -> str:
    area = json.loads((scen_dir.parents[1] / "area.json").read_text(encoding="utf-8"))
    return area.get("status", "available")


def test_versions_are_pinned():
    assert standards.AISVS_VERSION == "v1.0"
    assert standards.AST_VERSION == "v1.0-2026"


def test_aisvs_chapters_match_the_published_standard():
    assert {k: v["name"] for k, v in standards.AISVS_CHAPTERS.items()} == CHAPTERS
    assert sum(v["count"] for v in standards.AISVS_CHAPTERS.values()) == 191
    assert set(standards.AISVS_OUT_OF_SCOPE) == {"C1", "C3", "C4", "C11"}


def test_ast_names_match_the_published_list():
    assert standards.AST == AST_NAMES


def test_requirement_ids_are_well_formed_and_in_a_known_chapter():
    for rid, req in standards.AISVS_REQUIREMENTS.items():
        assert REQ_ID.match(rid), rid
        assert standards.aisvs_chapter(rid) in standards.AISVS_CHAPTERS, rid
        assert req["level"] in (1, 2, 3), rid
        assert 10 < len(req["summary"]) <= 120, f"{rid}: paraphrase should be one short line"


def test_every_control_citation_exists_and_is_earned():
    problems = []
    for ctrl in curriculum.CONTROLS:
        for m in ctrl.get("aisvs") or []:
            rid, strength, proof = m["id"], m["strength"], m.get("proven_by") or []
            where = f"{ctrl['id']} → {rid}"
            if rid not in standards.AISVS_REQUIREMENTS:
                problems.append(f"{where}: not in the registry")
                continue
            if strength not in standards.STRENGTHS:
                problems.append(f"{where}: unknown strength {strength!r}")
            if strength == "partial":
                continue
            if not proof:
                problems.append(f"{where}: 'demonstrates' with no proven_by")
            if standards.aisvs_chapter(rid) in standards.AISVS_OUT_OF_SCOPE:
                problems.append(f"{where}: demonstrated in an out-of-scope chapter")
            for path in proof:
                sid, _, step = path.partition("/")
                found = _scenario(sid)
                if not found:
                    problems.append(f"{where}: {sid} does not exist")
                    continue
                meta, sdir = found
                if _area_status(sdir) != "available":
                    problems.append(f"{where}: {sid} is in an area that is not available")
                if ctrl["id"] not in (meta.get("controls") or []):
                    problems.append(f"{where}: {sid} does not list {ctrl['id']} in controls")
                chk = sdir / "checks" / f"{step}.json"
                if not chk.exists():
                    problems.append(f"{where}: {path} has no graded check")
                    continue
                spec = json.loads(chk.read_text(encoding="utf-8"))
                if spec.get("kind") == "recall":
                    problems.append(f"{where}: {path} is a recall check (knowledge, not lab state)")
                if (spec.get("require_mode"), spec.get("expect")) != ("secure", "blocked"):
                    problems.append(f"{where}: {path} is not a secure-mode check that shows the control held")
    assert not problems, "\n".join(problems)


def test_ast_tags_exist():
    bad = []
    for ctrl in curriculum.CONTROLS:
        bad += [f"{ctrl['id']}: {a}" for a in ctrl.get("ast") or [] if a not in standards.AST]
    for meta in SCEN.glob("*/scenarios/*/scenario.json"):
        d = json.loads(meta.read_text(encoding="utf-8"))
        bad += [f"{d['id']}: {a}" for a in d.get("ast") or [] if a not in standards.AST]
    assert not bad, bad


def test_scenario_strength_never_exceeds_its_controls():
    by_id = {c["id"]: c for c in curriculum.CONTROLS}
    for meta in SCEN.glob("ai-security/scenarios/*/scenario.json"):
        d = json.loads(meta.read_text(encoding="utf-8"))
        for row in standards.scenario_aisvs(d["id"], d.get("controls") or [], curriculum.CONTROLS):
            if row["strength"] != "demonstrates":
                continue
            ok = any(
                m["id"] == row["id"] and m["strength"] == "demonstrates"
                and any(p.startswith(d["id"] + "/") for p in m.get("proven_by") or [])
                for cid in d.get("controls") or [] for m in by_id[cid].get("aisvs") or []
            )
            assert ok, f"{d['id']} shows {row['id']} as demonstrated without a proof in that scenario"


# Files that hold the registry itself, or the plan that drafted it, may use bare ids.
BARE_OK = {"lab/standards.py", "lab/curriculum.py", "PLAN.md", "tests/test_standards_registry.py"}
SCAN_ROOTS = ["content", "lab/ui", "docs", "README.md", "CHANGELOG.md"]
SKIP = ("docs/qa/", "docs/research/preview/")
DOTTED = re.compile(r"(?<![\w.])C\d{1,2}\.\d{1,2}\.\d{1,2}(?![\w.])")
AST_ID = re.compile(r"\bAST\d{2}\b")


def _files():
    for root in SCAN_ROOTS:
        p = ROOT / root
        items = [p] if p.is_file() else p.rglob("*")
        for f in items:
            if f.is_file() and f.suffix in {".md", ".json", ".html", ".js", ".py"}:
                rel = f.relative_to(ROOT).as_posix()
                if rel in BARE_OK or rel.startswith(SKIP):
                    continue
                yield rel, f.read_text(encoding="utf-8", errors="replace")


def test_every_aisvs_id_in_the_repo_is_prefixed_and_registered():
    bad = []
    for rel, text in _files():
        for m in DOTTED.finditer(text):
            rid = m.group(0)
            before = text[max(0, m.start() - 11):m.start()]
            if rid not in standards.AISVS_REQUIREMENTS:
                bad.append(f"{rel}: {rid} is not in lab/standards.py")
            elif before != "AISVS v1.0 ":
                bad.append(f"{rel}: write 'AISVS v1.0 {rid}', not a bare {rid} (lab controls are C1–C22 too)")
    assert not bad, "\n".join(bad[:40])


def test_every_ast_id_in_the_repo_is_registered():
    bad = []
    for rel, text in _files():
        bad += [f"{rel}: {a}" for a in AST_ID.findall(text) if a not in standards.AST]
    assert not bad, bad
