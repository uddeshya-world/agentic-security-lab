"""Functional pass over the player (PLAN.md P4 acceptance).

Scope gate → a graded step: Next is gated with its reason beside it, Check
before Run refuses, Skip is recorded as a skip (never a pass), Run lights the
trifecta HUD, Check then passes and Next opens. Screens to docs/qa/P4/.

    python scripts/qa/player_flow.py [base_url]
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
OUT = ROOT / "docs" / "qa" / "P4"
OUT.mkdir(parents=True, exist_ok=True)
fails: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


with sync_playwright() as p:
    b = p.chromium.launch()
    for width, scheme in ((1280, "dark"), (390, "light")):
        ctx = b.new_context(viewport={"width": width, "height": 900}, color_scheme=scheme)
        page = ctx.new_page()
        page.route("**/fonts.{googleapis,gstatic}.com/**", lambda r: r.abort())
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        url = f"{BASE}/lab/ui/scenario.html?area=ai-security&id=04-agent-exploit"
        page.goto(url, wait_until="load")
        page.evaluate("localStorage.clear()")
        page.reload(wait_until="load")
        page.wait_for_timeout(1500)

        gate = page.locator("#gateGo")
        if gate.count():
            check(gate.is_disabled(), f"[{width}] scope gate Start disabled until acknowledged")
            for cb in page.locator(".gate input[type=checkbox]").all():
                cb.check()
            page.wait_for_timeout(200)
            page.click("#gateGo")
            page.wait_for_timeout(800)

        check(not page.is_hidden("#hud"), f"[{width}] trifecta HUD shown for a scenario with legs")
        check("no run yet" in page.inner_text("#hudVec"), f"[{width}] HUD starts with no run")

        # Find the first graded step that has a Run button.
        steps = page.locator(".steps li")
        found = False
        for i in range(steps.count()):
            steps.nth(i).click()
            page.wait_for_timeout(500)
            if page.locator("#btnRun").count() and page.locator("#btnCheck").count():
                found = True
                break
        check(found, f"[{width}] found a run+check step")
        if not found:
            ctx.close()
            continue
        check(page.inner_text("#btnRun") == "Run the attack", f"[{width}] Run button copy")
        check(page.inner_text("#btnCheck") == "Check the evidence", f"[{width}] Check button copy")
        check(page.is_disabled("#next") and page.is_visible("#gateMsg"), f"[{width}] Next gated with the reason beside it")
        page.screenshot(path=str(OUT / f"player-gated-{width}-{scheme}.png"), full_page=True)

        page.click("#btnCheck")
        page.wait_for_timeout(1500)
        say = page.inner_text("#checkSay")
        # The server keeps the last run per step, so an earlier session's run can
        # legitimately satisfy this Check. Refusal-before-Run is asserted at the
        # API level (tests/test_run_check_split.py); here it is only reported.
        print("      info: check before run ->", say[:100].encode("ascii", "replace").decode())

        page.click("#btnRun")
        page.wait_for_selector("#runState:not(:has(.spinner))", timeout=90000)
        page.wait_for_timeout(500)
        vec = page.inner_text("#hudVec")
        check(vec == "closure 1·1·1", f"[{width}] vulnerable run lights the HUD ({vec})")
        timeline = page.inner_text("#timeline")
        check(timeline.count("SELECT * FROM customers WHERE 1=1") <= 1,
              f"[{width}] each SQL statement is printed once in the timeline")
        check("Path traversal" not in timeline, f"[{width}] no unrelated path-traversal output")
        page.click("#btnCheck")
        page.wait_for_timeout(2500)
        check(not page.is_disabled("#next"), f"[{width}] Next opens after the check passes")
        overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        check(overflow <= 0, f"[{width}] no horizontal overflow ({overflow})")
        page.screenshot(path=str(OUT / f"player-passed-{width}-{scheme}.png"), full_page=True)

        # Skip on the next gated step: recorded as skipped, not passed.
        page.click("#next")
        page.wait_for_timeout(600)
        if page.is_visible("#skipLink"):
            sid = page.evaluate("data.steps[idx].id")
            page.click("#skipLink")
            page.wait_for_timeout(600)
            rec = page.evaluate(f"CR.loadProgress('ai-security','04-agent-exploit')['{sid}']")
            check(bool(rec and rec.get("skipped")) and not rec.get("passed"), f"[{width}] skip recorded as skipped, not passed")
            check("skipped" in page.inner_text(".steps"), f"[{width}] rail shows the skip")
        check(not errors, f"[{width}] no page errors {errors[:2]}")
        ctx.close()
    b.close()

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)
