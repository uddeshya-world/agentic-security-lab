"""QA: claim the completion badge with a name, then verify it (fix batch F1).

Needs a lab whose server ledger already holds every Core pass (for example after
a full run). It claims through the real Area page UI, so it writes nothing the
ledger does not already have.

    python scripts/qa/badge_flow.py

Screenshots land in docs/qa/F1/.
"""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "qa" / "F1"
BASE = "http://127.0.0.1:8000"
failures = 0


def check(cond: bool, msg: str) -> None:
    global failures
    print(("ok   " if cond else "FAIL ") + msg)
    failures += 0 if cond else 1


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        for width, scheme in [(1280, "dark"), (390, "light")]:
            ctx = b.new_context(viewport={"width": width, "height": 900}, color_scheme=scheme)
            ctx.route("**/fonts.googleapis.com/**", lambda r: r.abort())
            ctx.route("**/fonts.gstatic.com/**", lambda r: r.abort())
            page = ctx.new_page()
            errors: list[str] = []
            page.on("pageerror", lambda e: errors.append(str(e)))

            page.goto(f"{BASE}/lab/ui/area.html?id=ai-security", wait_until="load")
            page.wait_for_selector("#claimBtn")
            check(page.locator(".credcard .emblem svg").count() == 1, f"[{width}] badge emblem on the credential card")
            state = page.locator(".credcard .emblem svg").get_attribute("aria-label") or ""
            check(("earned" in state) or ("locked" in state), f"[{width}] emblem state is written as a word ({state})")
            page.locator(".credcard").scroll_into_view_if_needed()
            page.locator(".credcard").screenshot(path=str(OUT / f"credcard-{width}-{scheme}.png"))

            page.click("#claimBtn")
            page.wait_for_selector("#learnerName")
            check(page.get_attribute("#learnerName", "maxlength") == "60", f"[{width}] name field capped at 60")
            page.fill("#learnerName", "First Student")
            page.screenshot(path=str(OUT / f"claim-form-{width}-{scheme}.png"))
            page.click("#nameForm button[type=submit]")
            page.wait_for_selector("#tok", timeout=30000)
            sheet = page.inner_text("#badgeBody")
            check("First Student" in sheet, f"[{width}] issued badge carries the typed name")
            check(page.locator("#badgeBody .emblem svg").count() == 1, f"[{width}] issued badge shows the emblem")
            check(page.locator("#dlBadge").count() == 1, f"[{width}] download button present")
            verify = page.locator("#badgeBody a.btn", has_text="Verify it")
            check(verify.count() == 1, f"[{width}] Verify it is a button")
            overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            check(overflow <= 0, f"[{width}] no horizontal overflow ({overflow})")
            page.screenshot(path=str(OUT / f"badge-issued-{width}-{scheme}.png"))

            with page.expect_download() as dl:
                page.click("#dlBadge")
            svg = Path(dl.value.path()).read_text(encoding="utf-8")
            check(svg.startswith("<svg") and "var(--" not in svg and "First Student" in svg,
                  f"[{width}] downloaded SVG is standalone (no CSS vars) and named")

            verify.click()
            page.wait_for_selector(".badgecard", timeout=30000)
            card = page.inner_text(".badgecard")
            check("valid signature" in card.lower() and "not valid" not in card.lower(), f"[{width}] verify page says valid")
            check("not verified" in card, f"[{width}] verify page labels the name as self-asserted")
            check(page.locator(".badgecard svg").count() == 1, f"[{width}] verify page shows the emblem")
            rows = page.locator(".badgecard tbody tr").count()
            check(rows == 23, f"[{width}] full transcript visible ({rows} rows)")
            page.screenshot(path=str(OUT / f"verify-{width}-{scheme}.png"), full_page=True)
            check(not errors, f"[{width}] no page errors {errors[:2]}")
            ctx.close()
        b.close()
    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
