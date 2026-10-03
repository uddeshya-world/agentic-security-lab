"""Guard the playground (lab/ui/play.html).

It has to stay a single static file that can be hosted anywhere, so it may not
load scripts or call an API. And its puzzle has to stay honest: the copy
promises a 3-point budget with an optimal answer at 2 points, so that is
recomputed here from the page's own CONTROLS and PATHS data, using a Python
port of the page's evaluator.

No Docker, no browser.
"""
from __future__ import annotations

import itertools
import re
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "lab" / "ui" / "play.html"
HTML = PAGE.read_text(encoding="utf-8")
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(|\bhsla?\(")


def _script() -> str:
    m = re.search(r"<script>(.*?)</script>", HTML, re.S)
    assert m, "play.html has no inline script"
    return m.group(1)


def _controls() -> list[dict]:
    src = _script()
    block = src[src.index("var CONTROLS = ["):src.index("var PATHS = [")]
    out = []
    for m in re.finditer(r'\{ id: "(\w+)".*?pts: (\d+), hard: (true|false), acts: \{([^}]*)\}', block, re.S):
        acts = {k: int(v) for k, v in re.findall(r"(\w): (\d)", m.group(4))}
        out.append({"id": m.group(1), "pts": int(m.group(2)), "hard": m.group(3) == "true", "acts": acts})
    return out


def _path_ids() -> list[str]:
    src = _script()
    block = src[src.index("var PATHS = ["):src.index("var picked")]
    return re.findall(r'\{ id: "(\w)"', block)


def _stops(path: str, picked: set[str], controls: list[dict]) -> bool:
    """Port of evaluate(): walk segments 0..3; the first hard control stops it."""
    for seg in range(4):
        for c in controls:
            if c["id"] in picked and c["acts"].get(path) == seg and c["hard"]:
                return True
    return False


def test_single_file_no_remote_scripts_no_api_calls():
    assert "<script src=" not in HTML
    assert "fetch(" not in HTML and "XMLHttpRequest" not in HTML
    assert not re.search(r'(src|href)="[^"]*cyberrange\.(css|js)', HTML), "play.html must not depend on shared assets"


def test_no_literal_colours_outside_token_declarations():
    offenders = []
    for n, line in enumerate(HTML.splitlines(), 1):
        if not HEX.search(line):
            continue
        if re.match(r"\s*--[a-z0-9-]+\s*:", line) or "&#" in line or "href=" in line:
            continue
        offenders.append(f"play.html:{n}: {line.strip()[:80]}")
    assert not offenders, "\n".join(offenders)


def test_level_two_data_matches_the_copy():
    controls = _controls()
    assert len(controls) == 7
    assert _path_ids() == ["A", "B", "C"]
    assert "var BUDGET = 3;" in _script()


def test_optimal_solution_costs_two_points_and_is_mail_plus_url():
    controls = _controls()
    by_id = {c["id"]: c for c in controls}
    paths = _path_ids()
    solutions = []
    for r in range(1, len(controls) + 1):
        for combo in itertools.combinations(by_id, r):
            cost = sum(by_id[c]["pts"] for c in combo)
            if cost > 3:
                continue
            if all(_stops(p, set(combo), controls) for p in paths):
                solutions.append((cost, set(combo)))
    assert solutions, "no set of controls within budget stops all three paths"
    best = min(cost for cost, _ in solutions)
    assert best == 2
    assert [s for c, s in solutions if c == best] == [{"mail", "url"}]


def test_soft_controls_never_stop_a_path():
    controls = _controls()
    soft = {c["id"] for c in controls if not c["hard"]}
    assert soft == {"inj", "spot", "rows"}
    for p in _path_ids():
        assert not _stops(p, soft, controls)


def test_level_four_has_exactly_two_correct_cuts():
    """Appendix A.4: pinning manifests and the recipient allow-list both hold."""
    src = _script()
    block = src[src.index("var L4OPTS = ["):src.index("var choice4")]
    chunks = block.split('{ id: "')[1:]
    ids = [c.split('"', 1)[0] for c in chunks]
    assert ids == ["ban", "prompt", "pin", "mail"]
    wins = [c.split('"', 1)[0] for c in chunks if "win: true" in c]
    assert wins == ["pin", "mail"]


def test_approved_strings_and_honesty_clause_present():
    for s in ("Everyone teaches you to break the agent. Here you decide",
              "Simulated agent · runs in your browser · synthetic data",
              "Many ways in, few ways out.",
              "Per-agent safety doesn",
              "A tool description is untrusted content with a better disguise."):
        assert s in HTML, s


def test_copy_rules():
    text = re.sub(r"<script>.*?</script>|<style>.*?</style>", "", HTML, flags=re.S)
    visible = re.sub(r"<[^>]+>", " ", text) + " " + _script()
    assert "—" not in visible, "no em-dash asides"
    for banned in ("revolutionary", "cutting-edge", "AI-powered", "employers trust", "certified"):
        assert banned.lower() not in visible.lower(), banned
    # No exclamation marks in prose (JS operators excluded by requiring a following space/quote end).
    assert not re.search(r"[A-Za-z]!(\s|\"|<)", visible), "no exclamation marks"
