"""Functional pass over the playground (PLAN.md P1.1, P1.3, P1.5).

1. Keyboard only: Tab to the level rail, arrow between tabs, complete all four
   levels with Enter/Space, and confirm the finish card appears.
2. Reviewer mode: switch, confirm questions are generated from the choices.
3. Reload restores progress; Reset clears it.
4. With localStorage throwing (a strict private window), the page still works.
5. Renders the Open Graph image from the level 3 closure screen.

    python scripts/qa/play_flow.py http://127.0.0.1:8000/lab/ui/play.html
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/lab/ui/play.html"
fails: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def press_until_focused(page, selector: str, limit: int = 80) -> None:
    for _ in range(limit):
        if page.evaluate("(s) => document.activeElement && document.activeElement.matches(s)", selector):
            return
        page.keyboard.press("Tab")
    raise AssertionError(f"could not Tab to {selector}")


def keyboard_run(page) -> None:
    page.goto(URL, wait_until="load")
    page.evaluate("localStorage.clear()")
    page.reload(wait_until="load")
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))

    press_until_focused(page, "#tab-1")
    page.keyboard.press("ArrowRight")
    check(page.evaluate("document.activeElement.id") == "tab-2", "ArrowRight moves focus to tab 2")
    check(page.get_attribute("#tab-2", "aria-selected") == "true", "tab 2 selected after ArrowRight")
    check(page.evaluate("document.getElementById('tab-1').tabIndex") == -1, "roving tabindex: tab 1 is -1")
    page.keyboard.press("End")
    check(page.evaluate("document.activeElement.id") == "tab-4", "End jumps to tab 4")
    page.keyboard.press("Home")
    page.keyboard.press("Enter")
    check(page.evaluate("document.activeElement.id") == "h-1", "Enter on a tab focuses the panel heading")

    # Level 1: Next hop five times, then "Go to level 2"
    press_until_focused(page, "#l1-next")
    for _ in range(5):
        page.keyboard.press("Enter")
    check(page.get_attribute("#hops .hop.cur", "aria-current") == "step", "current hop has aria-current=step")
    check("exfiltrated" in page.inner_text("#l1-main"), "level 1 ends in the exfiltration outcome")
    page.keyboard.press("Enter")
    check(page.evaluate("document.activeElement.id") == "h-2", "Go to level 2 moves focus to level 2 heading")

    # Level 2: Space on mail and url, then Run
    press_until_focused(page, "#ctl-mail"); page.keyboard.press("Space")
    press_until_focused(page, "#ctl-url"); page.keyboard.press("Space")
    check(page.inner_text("#budget-txt").startswith("2 / 3"), "budget shows 2 / 3 pts")
    press_until_focused(page, "#l2-run"); page.keyboard.press("Enter")
    check("optimal" in page.inner_text("#l2-result"), "mail + url reported as the optimal set")
    check(page.locator("#path-list .sr-only", has_text="stopped here").count() == 3, "each path has a screen-reader 'stopped here'")
    press_until_focused(page, "#to3"); page.keyboard.press("Enter")

    # Level 3: wrong answer first, then the cut
    press_until_focused(page, "#opts .opt"); page.keyboard.press("Enter")
    check("can't be sent" in page.inner_text("#vec-cap"), "firewall option explains the broken service")
    for _ in range(3):
        page.keyboard.press("Tab")
    page.keyboard.press("Enter")
    check(page.inner_text("#vec") == "(1, 1, 0)", "label cut gives (1, 1, 0)")
    check("Cut found" in page.inner_text("#opts"), "level 3 debrief shown")
    page.screenshot(path=str(ROOT / "docs" / "qa" / "P1" / "l3-closure.png"), full_page=False)
    press_until_focused(page, "#to4"); page.keyboard.press("Enter")

    # Level 4: wrong (prompt) then right (pin)
    press_until_focused(page, "#l4-opts .opt"); page.keyboard.press("Tab"); page.keyboard.press("Enter")
    check("Not provable" in page.inner_text("#l4-opts"), "prompt option marked not provable")
    page.keyboard.press("Tab"); page.keyboard.press("Enter")
    check("Two valid cuts" in page.inner_text("#l4-opts"), "pin option wins with the two-cuts debrief")
    check(page.is_visible("#finish"), "finish section appears after all four levels")
    share = page.input_value("#share-text")
    check("3 of 3 attacks" in share or "Stopped 3 of 3" in share, "share text carries the real level 2 result")
    check("{{" not in share, "share text has no unreplaced placeholder")
    check(not errors, f"no page errors ({errors[:2]})")

    # Reviewer mode
    page.click(".mode button[data-mode=reviewer]")
    qs = page.locator("#questions li")
    check(qs.count() == 4, f"reviewer questions: egress + composition + tools + skills (got {qs.count()})")
    check("AISVS v1.0 C7.3.3 (L2)" in page.inner_text("#questions"), "reviewer questions cite the AISVS requirement to ask for")
    check(page.is_visible("#print"), "print button visible in reviewer mode")
    check(not page.is_visible("#share-text"), "share card hidden in reviewer mode")
    page.screenshot(path=str(ROOT / "docs" / "qa" / "P1" / "reviewer-finish.png"), full_page=True)

    # Persistence
    page.reload(wait_until="load")
    check(page.inner_text("#st-4").startswith("✓"), "reload restores level 4 as done")
    check(page.get_attribute("html", "data-mode") == "reviewer", "reload restores reviewer mode")
    page.click("#reset")
    check(page.inner_text("#st-1").startswith("·"), "reset clears progress")
    page.click(".mode button[data-mode=learner]")


def storage_blocked(browser) -> None:
    ctx = browser.new_context()
    ctx.add_init_script("Object.defineProperty(window, 'localStorage', {get() { throw new Error('denied'); }});")
    page = ctx.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(URL, wait_until="load")
    for _ in range(5):
        page.click("#l1-next")
    check("exfiltrated" in page.inner_text("#l1-main"), "storage blocked: level 1 still completes")
    page.click("#reset")
    check(not errors, f"storage blocked: no page errors ({errors[:2]})")
    ctx.close()


def og_image(browser) -> None:
    ctx = browser.new_context(viewport={"width": 1200, "height": 630}, color_scheme="dark", device_scale_factor=1)
    page = ctx.new_page()
    page.goto(URL + "#level-3", wait_until="load")
    page.evaluate("localStorage.clear()")
    page.reload(wait_until="load")
    page.click("#tab-3")
    page.click("#opts .opt >> nth=3")
    page.add_style_tag(content=".bar,.hero,.rail,.panel-head,.foot,#opts .eyebrow,#opts .opt,#opts .row{display:none!important}"
                       ".wrap{padding-top:28px}.panel{border:0;background:none}"
                       ".l3{grid-template-columns:1.25fr 1fr!important;align-items:center}"
                       ".vec{font-size:56px!important}*{animation:none!important}")
    page.evaluate("""() => { const o = document.getElementById('opts');
      const h = document.createElement('div');
      h.innerHTML = '<p class="kick" style="font-family:var(--mono);font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--ash)">Place the Control · a MESA lab</p><h2 style="font-size:40px;margin:8px 0 16px">Three safe agents, one leak. Find the cut.</h2>';
      o.prepend(h); }""")
    page.evaluate("window.scrollTo(0, 0)")
    dest = ROOT / "lab" / "ui" / "assets" / "og-place-the-control.png"
    page.screenshot(path=str(dest), clip={"x": 0, "y": 0, "width": 1200, "height": 630})
    check(dest.exists() and dest.stat().st_size > 20000, f"OG image written ({dest.stat().st_size} bytes)")
    ctx.close()


with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    keyboard_run(ctx.new_page())
    ctx.close()
    storage_blocked(b)
    og_image(b)
    b.close()

print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)
