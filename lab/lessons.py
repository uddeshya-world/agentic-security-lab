"""Legacy lesson API — now a thin loader over ``content/areas/``.

Scenario folders are the single source of truth (see ``lab.content``). This
module reshapes them into the historical lesson dict so existing consumers
(``lab.simulate``, ``agents.app`` ``/lab/lessons``, ``lab/ui/index.html``)
keep working unchanged. Lesson ``id`` maps to the scenario's ``legacy_id``
(``l0``, ``a1`` …) so ``run_simulation`` and the console still resolve.
"""
from __future__ import annotations

from lab import content


def _to_lesson(scen: dict) -> dict:
    """Project a content scenario into the legacy lesson shape."""
    return {
        "id": scen.get("legacy_id") or scen.get("id"),
        "scenario_id": scen.get("id"),
        "area_id": scen.get("area_id"),
        "attack_id": scen.get("attack_id"),
        "title": scen.get("title"),
        "order": scen.get("order", 999),
        "owasp": scen.get("owasp") or [],
        "story": scen.get("summary") or (scen.get("intro_md") or "").strip(),
        "what_you_will_see": scen.get("summary") or "",
        "takeaway": scen.get("takeaway"),
        "design_rule": scen.get("design_rule"),
        "code_paths": scen.get("code_paths") or [],
        "mailhog": scen.get("mailhog", False),
    }


def get_lessons() -> list[dict]:
    """The legacy lesson list, as ``simulate.py`` and the sandbox console know it.

    Only scenarios that declare a ``legacy_id`` belong here — that field exists
    precisely to say "this answers to an older lesson id". Areas authored after
    the content migration have no legacy identity and must not appear, or they
    would collide with the ordering these two consumers depend on.
    """
    lessons = [_to_lesson(s) for s in content.list_scenarios() if s.get("legacy_id")]
    return sorted(lessons, key=lambda x: x["order"])


def get_lesson(lesson_id: str) -> dict | None:
    for scen in content.list_scenarios():
        if lesson_id in (scen.get("legacy_id"), scen.get("id"), scen.get("slug")):
            return _to_lesson(scen)
    return None
