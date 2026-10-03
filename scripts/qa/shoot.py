"""QA screenshots for lab/ui pages (PLAN.md §10).

For every page and every combination of width (390, 1280) and colour scheme
(light, dark): load it, save a full-page screenshot, and report horizontal
overflow and console errors. Optionally run axe-core if a local copy is given.

    python scripts/qa/shoot.py TASK_ID URL [URL ...] [--axe path/to/axe.min.js]

Screenshots land in docs/qa/<TASK_ID>/. Needs Playwright with Chromium.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]


def slug(url: str) -> str:
    tail = url.split("/lab/ui/")[-1] or "index"
    return re.sub(r"[^a-z0-9]+", "-", tail.lower()).strip("-")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--axe")
    ap.add_argument("--wait", type=int, default=800, help="ms to wait after load")
    a = ap.parse_args()
    out = ROOT / "docs" / "qa" / a.task
    out.mkdir(parents=True, exist_ok=True)
    axe_src = Path(a.axe).read_text(encoding="utf-8") if a.axe else None
    report, bad = [], 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for url in a.urls:
            for width in (390, 1280):
                for scheme in ("light", "dark"):
                    ctx = browser.new_context(viewport={"width": width, "height": 900}, color_scheme=scheme)
                    page = ctx.new_page()
                    errors: list[str] = []
                    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
                    page.on("pageerror", lambda e: errors.append(str(e)))
                    page.goto(url, wait_until="load", timeout=30000)
                    page.wait_for_timeout(a.wait)
                    overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                    name = f"{slug(url)}-{width}-{scheme}.png"
                    page.screenshot(path=str(out / name), full_page=True)
                    row = {"page": slug(url), "width": width, "scheme": scheme, "overflow": overflow,
                           "console_errors": [e for e in errors if "fonts.g" not in e]}
                    if axe_src and width == 1280:
                        page.add_script_tag(content=axe_src)
                        res = page.evaluate("axe.run(document, {resultTypes: ['violations']}).then(r => r.violations.map(v => ({id: v.id, impact: v.impact, n: v.nodes.length, sample: v.nodes[0] && v.nodes[0].target.join(' ')})))")
                        row["axe"] = res
                        row["axe_serious"] = [v for v in res if v["impact"] in ("serious", "critical")]
                    if overflow > 0 or row["console_errors"] or row.get("axe_serious"):
                        bad += 1
                    report.append(row)
                    ctx.close()
        browser.close()
    (out / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    for r in report:
        flag = "OK " if r["overflow"] <= 0 and not r["console_errors"] and not r.get("axe_serious") else "BAD"
        axe = f" axe serious/critical={len(r['axe_serious'])} all={len(r['axe'])}" if "axe" in r else ""
        print(f"{flag} {r['page']:28} {r['width']:4} {r['scheme']:5} overflow={r['overflow']} errors={len(r['console_errors'])}{axe}")
        for v in r.get("axe_serious", []):
            print(f"      axe {v['impact']}: {v['id']} x{v['n']} e.g. {v['sample']}")
        for e in r["console_errors"][:3]:
            print(f"      console: {e[:160]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
