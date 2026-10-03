"""Filesystem-backed content loader for Areas, scenarios and exploit prompts.

Scenario folders under ``content/areas/`` are the single source of truth for
lesson text. ``lab.lessons`` and ``lab.exploits`` are thin loaders over this
module so the existing ``/lab/lessons`` and ``/lab/exploits`` response shapes
survive the migration unchanged.

Layout::

    content/areas/<area>/area.json
    content/areas/<area>/exploits/<id>.json
    content/areas/<area>/scenarios/<slug>/scenario.json
    content/areas/<area>/scenarios/<slug>/step-01.md
    content/areas/<area>/scenarios/<slug>/checks/step-01.json

The lesson engine is environment-agnostic: it renders steps, runs checks and
tracks progress. What runs underneath is declared per Area in ``area.json``
(``env`` key), never assumed globally.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

CONTENT_ROOT = Path(__file__).resolve().parents[1] / "content" / "areas"


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def _load_all() -> dict[str, Any]:
    """Parse the whole content tree once. Call ``reload()`` to re-read."""
    areas: dict[str, Any] = {}
    if not CONTENT_ROOT.is_dir():
        return areas

    for area_dir in sorted(p for p in CONTENT_ROOT.iterdir() if p.is_dir()):
        meta_path = area_dir / "area.json"
        if not meta_path.is_file():
            continue
        area = _read_json(meta_path)
        area["id"] = area.get("id") or area_dir.name
        area["scenarios"] = _load_scenarios(area_dir / "scenarios", area["id"])
        area["exploits"] = _load_exploits(area_dir / "exploits")
        areas[area["id"]] = area
    return areas


def _load_scenarios(root: Path, area_id: str) -> list[dict[str, Any]]:
    if not root.is_dir():
        return []
    scenarios = []
    for slug_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        meta_path = slug_dir / "scenario.json"
        if not meta_path.is_file():
            continue
        scen = _read_json(meta_path)
        scen["id"] = scen.get("id") or slug_dir.name
        scen["area_id"] = area_id
        scen["slug"] = slug_dir.name
        scen["intro_md"] = _read_text(slug_dir / "intro.md")
        scen["finish_md"] = _read_text(slug_dir / "finish.md")
        scen["steps"] = _load_steps(slug_dir, scen.get("steps") or [])
        scenarios.append(scen)
    return sorted(scenarios, key=lambda s: s.get("order", 999))


def _load_steps(slug_dir: Path, declared: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach markdown body + check spec to each declared step."""
    steps = []
    for index, step in enumerate(declared):
        step = dict(step)
        step["index"] = index
        step["id"] = step.get("id") or f"step-{index + 1:02d}"
        step["body_md"] = _read_text(slug_dir / (step.get("file") or f"{step['id']}.md"))
        check_path = slug_dir / "checks" / f"{step['id']}.json"
        step["check"] = _read_json(check_path) if check_path.is_file() else None
        step["has_check"] = step["check"] is not None
        steps.append(step)
    return steps


def _run_spec(step: dict[str, Any]) -> dict[str, Any] | None:
    """What Run should do on this step.

    Taken from an explicit ``run`` key when the author declared one, otherwise
    derived from the step's check: a graded step that asserts a simulation in a
    given mode implies a Run button that performs exactly that simulation in
    exactly that mode. Deriving it keeps one fact in one place — change the
    check's ``require_mode`` and the Run button follows.
    """
    declared = step.get("run")
    if isinstance(declared, dict):
        return declared

    check = step.get("check") or {}
    sim = check.get("simulate")
    if not sim or check.get("kind") not in ("evidence", "simulate"):
        return None

    mode = check.get("require_mode") or "any"
    label = {
        "vulnerable": "Run the attack",
        "secure": "Run with the control on",
    }.get(mode, "Run it")
    return {"kind": "simulate", "simulate": sim, "mode": mode, "label": label}


def _client_check(step: dict[str, Any]) -> dict[str, Any] | None:
    """The part of a check spec the browser is allowed to see.

    A recall question ships its prompt and its options. It never ships ``answer``,
    and it never ships ``asserts`` either — for a recall check, the asserts describe
    what the question is testing, which is the answer key by another name.
    """
    check = step.get("check")
    if not check:
        return None
    kind = (check.get("kind") or "manual").lower()
    out: dict[str, Any] = {"kind": kind}
    if kind == "recall":
        out["prompt"] = check.get("prompt")
        out["options"] = check.get("options") or []
    else:
        out["require_mode"] = check.get("require_mode") or "any"
        out["expect"] = check.get("expect")
        out["asserts"] = check.get("asserts") or []
    return out


def _load_exploits(root: Path) -> list[dict[str, Any]]:
    if not root.is_dir():
        return []
    exploits = []
    for path in sorted(root.glob("*.json")):
        item = _read_json(path)
        item["id"] = item.get("id") or path.stem
        exploits.append(item)
    return sorted(exploits, key=lambda e: e.get("order", 999))


def reload() -> None:
    """Drop the parse cache so edited content is picked up without a restart."""
    _load_all.cache_clear()


def list_areas() -> list[dict[str, Any]]:
    return list(_load_all().values())


def get_area(area_id: str) -> dict[str, Any] | None:
    return _load_all().get(area_id)


def list_scenarios(area_id: str | None = None) -> list[dict[str, Any]]:
    if area_id:
        area = get_area(area_id)
        return list(area.get("scenarios") or []) if area else []
    out: list[dict[str, Any]] = []
    for area in _load_all().values():
        out.extend(area.get("scenarios") or [])
    return out


def get_scenario(area_id: str, scenario_id: str) -> dict[str, Any] | None:
    for scen in list_scenarios(area_id):
        if scenario_id in (scen.get("id"), scen.get("slug"), scen.get("legacy_id")):
            return scen
    return None


def find_scenario(scenario_id: str) -> dict[str, Any] | None:
    """Look a scenario up across every Area, by id, slug or legacy lesson id."""
    for scen in list_scenarios():
        if scenario_id in (scen.get("id"), scen.get("slug"), scen.get("legacy_id")):
            return scen
    return None


def get_step(area_id: str, scenario_id: str, step_id: str) -> dict[str, Any] | None:
    scen = get_scenario(area_id, scenario_id)
    if not scen:
        return None
    for step in scen.get("steps") or []:
        if step["id"] == step_id:
            return step
    return None


def list_exploits_raw() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for area in _load_all().values():
        out.extend(area.get("exploits") or [])
    return out


def _check_kind_counts(scenario: dict[str, Any]) -> dict[str, int]:
    """Count graded steps by check kind for one scenario."""
    counts: dict[str, int] = {}
    for step in scenario.get("steps") or []:
        if not step.get("has_check"):
            continue
        kind = (step.get("check") or {}).get("kind") or "manual"
        counts[kind] = counts.get(kind, 0) + 1
    return counts


def catalog_payload() -> dict[str, Any]:
    """Killercoda-style Area tiles: what it teaches, who it is for, what it maps to."""
    areas = []
    for area in list_areas():
        scenarios = area.get("scenarios") or []
        areas.append(
            {
                "id": area["id"],
                "title": area.get("title"),
                "blurb": area.get("blurb"),
                "status": area.get("status", "available"),
                "icon": area.get("icon"),
                "difficulty": area.get("difficulty"),
                "certs": area.get("certs") or [],
                "roles": area.get("roles") or [],
                "outcomes": area.get("outcomes") or [],
                "prerequisites": area.get("prerequisites") or [],
                "long_description": area.get("long_description"),
                "credential": area.get("credential"),
                "env": area.get("env"),
                "scenario_count": len(scenarios),
                "estimated_minutes": sum(s.get("est_minutes") or 0 for s in scenarios),
                "scenarios": [
                    {
                        "id": s["id"],
                        "slug": s.get("slug"),
                        "title": s.get("title"),
                        "order": s.get("order"),
                        "difficulty": s.get("difficulty"),
                        "est_minutes": s.get("est_minutes"),
                        "summary": s.get("summary"),
                        "owasp": s.get("owasp") or [],
                        "track": s.get("track") or "core",
                        "step_count": len(s.get("steps") or []),
                        "graded_steps": sum(1 for st in s.get("steps") or [] if st.get("has_check")),
                        # Per-kind counts so the catalog can describe a scenario's real
                        # composition. A `recall` check is answered from the reading; every
                        # other kind asserts lab state the learner had to produce by running
                        # the attack first. Without this split the tile can only say "graded".
                        "check_kinds": _check_kind_counts(s),
                    }
                    for s in scenarios
                ],
            }
        )
    return {
        "areas": sorted(areas, key=lambda a: (a.get("status") != "available", a.get("title") or "")),
        "area_count": len(areas),
        "scenario_count": sum(a["scenario_count"] for a in areas),
    }


def scenario_payload(area_id: str, scenario_id: str) -> dict[str, Any] | None:
    """Full scenario for the stepper: metadata + ordered steps with rendered bodies."""
    scen = get_scenario(area_id, scenario_id)
    if not scen:
        return None
    area = get_area(area_id) or {}
    return {
        "area": {
            "id": area.get("id"),
            "title": area.get("title"),
            "env": area.get("env"),
            "credential": area.get("credential"),
        },
        "id": scen["id"],
        "slug": scen.get("slug"),
        "legacy_id": scen.get("legacy_id"),
        "title": scen.get("title"),
        "summary": scen.get("summary"),
        "order": scen.get("order"),
        "difficulty": scen.get("difficulty"),
        "est_minutes": scen.get("est_minutes"),
        "owasp": scen.get("owasp") or [],
        "track": scen.get("track") or "core",
        "controls": scen.get("controls") or [],
        # Optional trifecta legs the scenario's attack path touches: any of "u", "p", "e".
        "legs": [leg for leg in (scen.get("legs") or []) if leg in ("u", "p", "e")],
        "attack_id": scen.get("attack_id"),
        "mailhog": scen.get("mailhog", False),
        "code_paths": scen.get("code_paths") or [],
        "takeaway": scen.get("takeaway"),
        "design_rule": scen.get("design_rule"),
        "intro_md": scen.get("intro_md"),
        "finish_md": scen.get("finish_md"),
        "steps": [
            {
                "id": st["id"],
                "index": st["index"],
                "title": st.get("title"),
                "body_md": st.get("body_md"),
                "has_check": st.get("has_check", False),
                "check_kind": (st.get("check") or {}).get("kind"),
                "check": _client_check(st),
                "hint": st.get("hint"),
                "run": _run_spec(st),
                "mode": st.get("mode"),
                "optional": st.get("optional", False),
                "ungraded_live": st.get("ungraded_live", False),
            }
            for st in scen.get("steps") or []
        ],
    }
