"""QA: the Watch button in a Core lesson (fix batch F2).

    python scripts/qa/video_flow.py [--local-mp4 DIR]

With --local-mp4, requests for the Pages MP4s are answered from DIR (for testing
before a deploy). Always also tests the offline path by blocking the Pages URL.
Screenshots land in docs/qa/F2/.
"""
from __future__ import annotations

import argparse
import sys

sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "qa" / "F2"
BASE = "http://127.0.0.1:8000"
PAGES = "https://uddeshya-world.github.io/agentic-security-lab/video/"
failures = 0


def check(cond: bool, msg: str) -> None:
    global failures
    print(("ok   " if cond else "FAIL ") + msg)
    failures += 0 if cond else 1


def open_lesson(ctx, sid):
    page = ctx.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"{BASE}/lab/ui/scenario.html?area=ai-security&id={sid}", wait_until="load")
    page.wait_for_timeout(1200)
    if page.locator("#gateGo").count():
        for cb in page.locator(".gate input[type=checkbox]").all():
            cb.check()
        page.click("#gateGo")
        page.wait_for_timeout(600)
    return page, errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--local-mp4")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for width, scheme in [(1280, "dark"), (390, "light")]:
            ctx = b.new_context(viewport={"width": width, "height": 900}, color_scheme=scheme)
            ctx.route("**/fonts.g*/**", lambda r: r.abort())
            if a.local_mp4:
                local = Path(a.local_mp4)

                def serve(route, _request=None):
                    name = route.request.url.rsplit("/", 1)[-1]
                    route.fulfill(path=str(local / name), content_type="video/mp4")
                ctx.route(PAGES + "*.mp4", serve)
            page, errors = open_lesson(ctx, "01-tool-abuse-sqli")
            btn = page.locator("blockquote.plain .watch")
            check(btn.count() == 1, f"[{width}] Watch button inside the analogy box")
            check("1:25" in btn.inner_text(), f"[{width}] button shows the length ({btn.inner_text()})")
            check(page.evaluate("document.querySelector('video') === null"), f"[{width}] nothing loads before Watch")
            btn.click()
            page.wait_for_selector("#videoSheet[open] video")
            check(page.get_attribute("#videoSheet video", "autoplay") is None, f"[{width}] no autoplay")
            src = page.get_attribute("#videoSheet video source", "src")
            check(src == PAGES + "01-tool-abuse-sqli.mp4", f"[{width}] streams from Pages")
            page.wait_for_function("document.querySelector('[data-tx]').textContent.length > 200", timeout=10000)
            check("library request slip" in (page.text_content("[data-tx]") or ""), f"[{width}] transcript loaded from the lab")
            if a.local_mp4:
                page.wait_for_function("document.querySelector('#videoSheet video').readyState >= 1", timeout=20000)
                dur = page.evaluate("document.querySelector('#videoSheet video').duration")
                check(84 < dur < 87, f"[{width}] video metadata loads ({dur:.1f} s)")
            overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            check(overflow <= 0, f"[{width}] no horizontal overflow ({overflow})")
            page.screenshot(path=str(OUT / f"watch-{width}-{scheme}.png"))
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
            check(not page.evaluate("document.getElementById('videoSheet').open"), f"[{width}] Escape closes the dialog")
            check(not errors, f"[{width}] no page errors {errors[:2]}")
            ctx.close()

            # Offline: the Pages URL fails, the lesson says so and the transcript still works.
            ctx = b.new_context(viewport={"width": width, "height": 900}, color_scheme=scheme)
            ctx.route("**/fonts.g*/**", lambda r: r.abort())
            ctx.route(PAGES + "**", lambda r: r.abort())
            page, errors = open_lesson(ctx, "17-data-guards")
            page.locator("blockquote.plain .watch").click()
            page.wait_for_selector("#videoSheet [data-err]:not([hidden])", timeout=15000)
            check(True, f"[{width}] offline: says the video needs an internet connection")
            page.wait_for_function("document.querySelector('[data-tx]').textContent.length > 200", timeout=10000)
            check("airport" in (page.text_content("[data-tx]") or "").lower(), f"[{width}] offline: transcript still there")
            page.screenshot(path=str(OUT / f"watch-offline-{width}-{scheme}.png"))
            ctx.close()

            # A scenario with no video shows no button.
            ctx = b.new_context(viewport={"width": width, "height": 900}, color_scheme=scheme)
            ctx.route("**/fonts.g*/**", lambda r: r.abort())
            page, _ = open_lesson(ctx, "19-mcp-tool-poisoning")
            check(page.locator(".watch").count() == 0, f"[{width}] no Watch button without a video")
            ctx.close()
        b.close()
    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
