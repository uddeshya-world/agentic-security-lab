"""Guard the 2026 OWASP renumbering across the whole repo.

The 2026 list (renumbered 4 Aug 2026) *swapped meanings* with 2025 for eight of ten
ids -- most dangerously LLM03 and LLM06, which traded places:

    2025 LLM06 Excessive Agency        -> 2026 LLM03
    2025 LLM03 Supply Chain            -> 2026 LLM04
    2025 LLM04 Data and Model Poisoning-> 2026 LLM05
    2025 LLM05 Improper Output Handling-> 2026 LLM10
    2025 LLM07 System Prompt Leakage   -> 2026 LLM08 Hidden Context Exposure
    2025 LLM08 Vector and Embedding    -> 2026 LLM09
    2025 LLM09 Misinformation          -> 2026 LLM07
    2025 LLM10 Unbounded Consumption   -> 2026 LLM06

That means a *bare* id is unauditable: reading `LLM06` tells you nothing about which
scheme it is in, so a stale one cannot be spotted by eye and a blind find/replace would
silently invert already-correct files. The defence is to require that wherever an id is
written next to a category name, the pairing is the 2026 one. This test enforces that
repo-wide, so the next person to add content cannot reintroduce a 2025 mapping.
"""
from __future__ import annotations

import re
from pathlib import Path

from lab import content, curriculum

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", "chroma_data", ".venv"}
SUFFIXES = {".py", ".md", ".json", ".html", ".js"}

# Files whose job is to *talk about* the renumbering, so they legitimately contain
# 2025 pairings. Each is allow-listed for a stated reason, not blanket-ignored.
ALLOWED = {
    "docs/AI-AGENT-SECURITY-CURRICULUM.md",   # holds the 2025 -> 2026 crosswalk table
    "docs/CURRICULUM-REVIEW-2026-09-06.md",   # quotes the stale values as review findings
    "docs/research/CURRICULUM-RESEARCH-PROMPT.md",
    "tests/test_owasp_2026_consistency.py",   # this file
}

NAMES_2025 = {
    "LLM03": "Supply Chain",
    "LLM04": "Data and Model Poisoning",
    "LLM05": "Improper Output Handling",
    "LLM06": "Excessive Agency",
    "LLM07": "System Prompt Leakage",
    "LLM08": "Vector and Embedding",
    "LLM09": "Misinformation",
    "LLM10": "Unbounded Consumption",
}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z]", "", s.lower())


def _repo_files():
    for p in ROOT.rglob("*"):
        if p.suffix not in SUFFIXES or not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel in ALLOWED:
            continue
        yield rel, p


def test_no_2025_id_name_pairings_anywhere():
    """No file may pair an id with the name that id carried in 2025."""
    pat = re.compile(r"\b(LLM\d{2})\b[ :\u2014\-]*([A-Za-z][A-Za-z/ \-&]{2,40})?")
    offenders = []
    for rel, path in _repo_files():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, 1):
            if "was llm" in line.lower():          # explicit historical annotation ("Was LLM07 ... in 2025")
                continue
            for m in pat.finditer(line):
                lid, name = m.group(1), (m.group(2) or "").strip()
                if lid not in NAMES_2025 or not name:
                    continue
                stale, current = _norm(NAMES_2025[lid]), _norm(curriculum.OWASP_LLM[lid]["name"])
                if current.startswith(stale[:12]):  # unchanged between years
                    continue
                if _norm(name).startswith(stale[:12]):
                    offenders.append(f"{rel}:{n}  {lid} \"{name}\" is the 2025 name")
    assert not offenders, "2025 OWASP pairings found:\n" + "\n".join(offenders)


def test_controls_agree_with_the_scenarios_they_stop():
    """Every id a control claims must be declared by some scenario it stops.

    C1-C17 predate the renumbering, so this pins them: a stale edit fails here instead
    of quietly mislabelling the remediation panel. A control whose `stops` list names
    only roadmap modules (`m3`, `m4`, ...) has no authored scenario to agree with yet,
    so it is exempt until that module ships.
    """
    declared = set()
    for area in ("ai-security", "blue-team"):
        for scen in content.list_scenarios(area):
            for tag in scen.get("owasp") or []:
                declared.add(tag.split(":")[0].split()[0])

    def is_roadmap_only(ctrl):
        stops = ctrl.get("stops") or []
        return bool(stops) and all(re.fullmatch(r"m\d+", str(x)) for x in stops)

    unknown = {}
    for ctrl in curriculum.CONTROLS:
        if is_roadmap_only(ctrl):
            continue
        for cid in ctrl.get("owasp") or []:
            if cid.startswith("LLM") and cid not in declared:
                unknown.setdefault(cid, []).append(ctrl["id"])
    assert not unknown, f"controls cite LLM ids no scenario declares: {unknown}"


def test_excessive_agency_is_llm03_everywhere_it_is_named():
    """The single most confusable pair, asserted directly."""
    assert curriculum.OWASP_LLM["LLM03"]["name"] == "Excessive Agency"
    assert curriculum.OWASP_LLM["LLM06"]["name"] == "Unbounded Consumption"
    for ctrl in curriculum.CONTROLS:
        if ctrl["id"] in {"C1", "C2", "C3", "C5", "C7", "C10", "C14", "C16"}:
            assert "LLM03" in ctrl["owasp"], f"{ctrl['id']} lost its Excessive Agency tag"
            assert "LLM06" not in ctrl["owasp"], f"{ctrl['id']} still carries the 2025 id"


def test_difficulty_uses_one_vocabulary():
    """Two scales in one catalog make tiles from different Areas incomparable.

    `AREA_TEMPLATE.md` pins four rungs; this fails the build if a synonym creeps back.
    """
    allowed = {"beginner", "intermediate", "advanced", "expert"}
    bad = {}
    for area in ("ai-security", "blue-team"):
        for scen in content.list_scenarios(area):
            d = scen.get("difficulty")
            if d and d not in allowed:
                bad[f"{area}/{scen['id']}"] = d
    assert not bad, f"difficulty values outside {sorted(allowed)}: {bad}"


def test_every_scenario_closes_with_a_finish_page():
    """A learner who finishes a lab with no closing summary just stops mid-air."""
    missing = [
        f"{area}/{scen['id']}"
        for area in ("ai-security", "blue-team")
        for scen in content.list_scenarios(area)
        if not (ROOT / "content" / "areas" / area / "scenarios" / scen["id"] / "finish.md").exists()
    ]
    assert not missing, f"scenarios with no finish.md: {missing}"


def test_data_path_hops_agree_with_controls_and_stages():
    """The hop map the landing page renders must stay tied to the real catalogs.

    It is lifted out of `05-guardrail-map`'s markdown so the UI has one source
    instead of a retyped table; these assertions are what stop the two from
    drifting the way the OWASP ids did.
    """
    hops = curriculum.DATA_PATH_HOPS
    assert len(hops) == 8, f"the guardrail map teaches eight hops, found {len(hops)}"
    assert [h["n"] for h in hops] == list(range(1, 9)), "hops must be numbered 1-8 in order"

    control_ids = {c["id"] for c in curriculum.CONTROLS}
    orphans = {
        h["n"]: [c for c in h["controls"] if c not in control_ids]
        for h in hops
        if any(c not in control_ids for c in h["controls"])
    }
    assert not orphans, f"hops cite controls that do not exist: {orphans}"

    # `stage` keys into the six-stage trace the UI draws, so a typo here would
    # silently drop a hop off the diagram rather than raise.
    stages = {"user", "rag", "planner", "executor", "tools", "world"}
    bad = {h["n"]: h["stage"] for h in hops if h["stage"] not in stages}
    assert not bad, f"hops name stages the trace does not have: {bad}"

    # Every hop must name where the control actually lives, or it is a slogan.
    assert all(h.get("code") for h in hops), "every hop needs a code pointer"
