#!/usr/bin/env python3
"""Playwright captures of the live CyberRange lab (dark theme, 1920×1080)."""
from __future__ import annotations

import time
from pathlib import Path

LAB = "http://127.0.0.1:8000"
AREA = "ai-security"
VIEWPORT = {"width": 1920, "height": 1080}

# scenario_id -> list of capture specs
# Each spec: id, step (1-based UI step index or step-id), mode, action
CAPTURE_PLAN = {
    "00-orientation": [
        {"id": "area", "kind": "area"},
        {"id": "scenario-map", "kind": "scenario", "step": "step-01"},
    ],
    "01-tool-abuse-sqli": [
        {"id": "scenario", "kind": "scenario", "step": "step-01"},
        {"id": "vuln-run", "kind": "run", "step": "step-02", "mode": "vulnerable"},
        {"id": "secure-run", "kind": "run", "step": "step-05", "mode": "secure"},
    ],
    "16-direct-injection": [
        {"id": "scenario", "kind": "scenario", "step": "step-01"},
        {"id": "vuln-run", "kind": "run", "step": "step-02", "mode": "vulnerable"},
        {"id": "secure-run", "kind": "run", "step": "step-03", "mode": "secure"},
    ],
    "02-rag-poisoning": [
        {"id": "scenario", "kind": "scenario", "step": "step-01"},
        {"id": "vuln-run", "kind": "run", "step": "step-03", "mode": "vulnerable"},
        {"id": "secure-run", "kind": "run", "step": "step-05", "mode": "secure"},
    ],
    "03-cross-tool-exfil": [
        {"id": "scenario", "kind": "scenario", "step": "step-01"},
        {"id": "vuln-run", "kind": "run", "step": "step-02", "mode": "vulnerable", "clear_mailhog": True},
        {"id": "mailhog", "kind": "mailhog"},
        {"id": "secure-run", "kind": "run", "step": "step-05", "mode": "secure"},
    ],
    "17-data-guards": [
        {"id": "scenario", "kind": "scenario", "step": "step-01"},
        {"id": "vuln-run", "kind": "run", "step": "step-02", "mode": "vulnerable"},
        {"id": "secure-run", "kind": "run", "step": "step-03", "mode": "secure"},
        {"id": "forensics", "kind": "run", "step": "step-03", "mode": "secure", "tab": "forensics"},
    ],
    "18-agent-identity": [
        {"id": "scenario", "kind": "scenario", "step": "step-01"},
        {"id": "vuln-run", "kind": "run", "step": "step-02", "mode": "vulnerable"},
        {"id": "secure-run", "kind": "run", "step": "step-03", "mode": "secure"},
    ],
    "04-agent-exploit": [
        {"id": "scenario", "kind": "scenario", "step": "step-01"},
        {"id": "vuln-run", "kind": "run", "step": "step-02", "mode": "vulnerable"},
        {"id": "secure-run", "kind": "run", "step": "step-05", "mode": "secure"},
    ],
    "05-guardrail-map": [
        {"id": "scenario", "kind": "scenario", "step": "step-01"},
        {"id": "run-map", "kind": "run", "step": "step-02", "mode": "vulnerable"},
    ],
}


def _force_dark(page) -> None:
    page.add_init_script("""
        try {
          localStorage.setItem('cr:theme', 'dark');
          // Dismiss the per-Area scope gate so lessons render immediately.
          localStorage.setItem('cr.scope.ai-security', '1');
        } catch (e) {}
    """)
    page.emulate_media(color_scheme="dark")


def _dismiss_gate_if_present(page) -> None:
    gate = page.locator("#gateGo")
    if not gate.count():
        return
    try:
        if not gate.is_visible():
            return
    except Exception:
        return
    for sel in ("#gateSynthetic", "#gateOwn"):
        box = page.locator(sel)
        if box.count():
            try:
                box.check(force=True)
            except Exception:
                page.evaluate(f"() => {{ const el=document.querySelector('{sel}'); if(el) el.checked=true; el&&el.dispatchEvent(new Event('change',{{bubbles:true}})); }}")
    page.wait_for_timeout(200)
    if gate.count() and gate.is_enabled():
        gate.click()
        page.wait_for_timeout(700)


def _step_index(step: str | None) -> int | None:
    if not step:
        return None
    import re
    m = re.search(r"step-0*([0-9]+)", step)
    if not m:
        return None
    return int(m.group(1)) - 1  # step-01 -> 0


def _goto_scenario(page, scenario_id: str, step: str | None = None) -> None:
    url = f"{LAB}/lab/ui/scenario.html?area={AREA}&id={scenario_id}"
    page.goto(url, wait_until="networkidle", timeout=60000)
    page.evaluate("""() => {
        document.documentElement.setAttribute('data-theme', 'dark');
        try {
          localStorage.setItem('cr:theme', 'dark');
          localStorage.setItem('cr.scope.ai-security', '1');
        } catch (e) {}
    }""")
    page.wait_for_timeout(300)
    _dismiss_gate_if_present(page)
    # If gate was shown despite localStorage, reload once so scopeAcknowledged() is true
    if page.locator("#gateGo").count() and page.locator("#gateGo").is_visible():
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(400)
        _dismiss_gate_if_present(page)
    idx = _step_index(step)
    if idx is not None:
        page.evaluate("""(i) => { if (typeof go === 'function') go(i); }""", idx)
        page.wait_for_timeout(500)
    # Wait until lesson body is present
    try:
        page.wait_for_selector("#body, #btnRun, .act", timeout=10000)
    except Exception:
        pass


def _set_mode(page, mode: str) -> None:
    btn = page.locator(f'button[data-mode="{mode}"]')
    if btn.count():
        btn.first.click()
        page.wait_for_timeout(200)
        return
    label = "VULNERABLE" if mode == "vulnerable" else "SECURE"
    alt = page.get_by_role("button", name=label)
    if alt.count():
        alt.first.click()
        page.wait_for_timeout(200)


def _click_run(page) -> None:
    page.wait_for_timeout(300)
    # Ensure run act is rendered
    if not page.locator("#btnRun").count():
        # Maybe wrong step — dump hint
        raise RuntimeError("Run button not found (is this a run step?)")
    page.locator("#btnRun").first.click()
    page.wait_for_timeout(1200)
    try:
        page.wait_for_function(
            """() => {
                const t = document.getElementById('timeline');
                if (!t) return false;
                return t.innerText.length > 80 && !t.innerText.includes('No run on this step');
            }""",
            timeout=25000,
        )
    except Exception:
        page.wait_for_timeout(2000)


def _frame_mailhog(page, raw: Path, dest: Path) -> None:
    """Place the sanitized MailHog list inside a dark CyberRange frame."""
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=JetBrains+Mono:wght@500&display=swap');
    html,body{{margin:0;width:1920px;height:1080px;background:#0a0c10;color:#e9ecf1;font-family:'Space Grotesk',sans-serif}}
    .wrap{{padding:64px 80px}}
    .k{{font:500 14px 'JetBrains Mono',monospace;letter-spacing:.1em;text-transform:uppercase;color:#ffb598;
       border:1px solid #5e2a14;background:#341409;display:inline-block;padding:8px 14px;border-radius:999px}}
    h1{{font-size:44px;margin:24px 0 8px}}
    p{{font:500 22px 'JetBrains Mono',monospace;color:#8b94a3;margin:0 0 28px}}
    .shot{{border:1px solid #364150;border-radius:12px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.5)}}
    .shot img{{display:block;width:100%}}
    </style></head><body><div class="wrap">
    <span class="k">Exfil proof</span>
    <h1>MailHog: the lab's stand-in attacker inbox</h1>
    <p>127.0.0.1:8025 · to audit@external-logging.test · "Customer Export Lab M01"</p>
    <div class="shot"><img src="{raw.resolve().as_uri()}"></div>
    </div></body></html>"""
    tmp = dest.with_name("mailhog-frame.html")
    tmp.write_text(html, encoding="utf-8")
    page.goto(tmp.resolve().as_uri(), wait_until="networkidle")
    page.screenshot(path=str(dest))


def _shot(page, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(path), full_page=False)
    return path


def capture_all(out_dir: Path, only: list[str] | None = None) -> dict[str, dict[str, Path]]:
    from playwright.sync_api import sync_playwright

    out_dir = Path(out_dir)
    results: dict[str, dict[str, Path]] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=VIEWPORT,
            device_scale_factor=2,  # 3840x2160 for crisp zooms
            color_scheme="dark",
        )
        page = context.new_page()
        _force_dark(page)

        for scenario, specs in CAPTURE_PLAN.items():
            if only and scenario not in only:
                continue
            results[scenario] = {}
            sdir = out_dir / scenario
            sdir.mkdir(parents=True, exist_ok=True)
            print(f"[capture] {scenario}", flush=True)

            for spec in specs:
                cid = spec["id"]
                dest = sdir / f"{cid}.png"
                kind = spec["kind"]
                try:
                    if kind == "area":
                        page.goto(f"{LAB}/lab/ui/area.html?id={AREA}", wait_until="networkidle", timeout=60000)
                        page.evaluate("""() => document.documentElement.setAttribute('data-theme','dark')""")
                        page.wait_for_timeout(600)
                        _shot(page, dest)
                    elif kind == "mailhog":
                        page.goto("http://127.0.0.1:8025", wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_timeout(1200)
                        # No third-party logos: hide MailHog brand mark, GitHub link and Jim panel.
                        page.add_style_tag(content="""
                          .navbar-brand img, .navbar-brand svg, a[href*="github"], .jim, #jim,
                          .navbar-right, [ng-show*="jim"], .well { display:none !important; }
                          .navbar-brand { visibility:hidden !important; }
                        """)
                        page.evaluate("""() => {
                          for (const el of document.querySelectorAll('div,section,aside')) {
                            const tx = (el.innerText||'').trim();
                            if (/^Jim\b/.test(tx) && tx.length < 200) el.style.display='none';
                          }
                        }""")
                        page.wait_for_timeout(200)
                        raw = dest.with_name("mailhog-raw.png")
                        page.screenshot(path=str(raw), clip={"x": 0, "y": 0, "width": 1920, "height": 560})
                        _frame_mailhog(page, raw, dest)
                    elif kind == "scenario":
                        _goto_scenario(page, scenario, spec.get("step"))
                        page.wait_for_timeout(500)
                        _shot(page, dest)
                    elif kind == "run":
                        if spec.get("clear_mailhog"):
                            # Empty the local MailHog sink so the exfil run shows exactly one new message.
                            import urllib.request
                            req = urllib.request.Request("http://127.0.0.1:8025/api/v1/messages", method="DELETE")
                            try:
                                urllib.request.urlopen(req, timeout=10).read()
                            except Exception as e:
                                print(f"  (mailhog clear skipped: {e})", flush=True)
                        _goto_scenario(page, scenario, spec.get("step"))
                        mode = spec.get("mode", "vulnerable")
                        _set_mode(page, mode)
                        _click_run(page)
                        if spec.get("tab") == "forensics":
                            # Try to open a Forensics tab if present
                            for label in ("Forensics", "forensics", "Evidence"):
                                tab = page.get_by_text(label, exact=False)
                                if tab.count():
                                    try:
                                        tab.first.click()
                                        page.wait_for_timeout(400)
                                        break
                                    except Exception:
                                        pass
                        # Prefer scrolling timeline into view
                        page.evaluate("""() => {
                            const t = document.getElementById('timeline');
                            if (t) t.scrollIntoView({block:'center'});
                        }""")
                        page.wait_for_timeout(300)
                        _shot(page, dest)
                    results[scenario][cid] = dest
                    print(f"  ok {cid} -> {dest.name}", flush=True)
                except Exception as e:
                    print(f"  FAIL {cid}: {e}", flush=True)
                    # Write a placeholder dark frame via page content
                    page.set_content(
                        f"<html><body style='margin:0;background:#0a0c10;color:#e9ecf1;"
                        f"font:600 32px sans-serif;display:grid;place-items:center;height:100vh'>"
                        f"Capture failed: {scenario}/{cid}</body></html>"
                    )
                    _shot(page, dest)
                    results[scenario][cid] = dest

        browser.close()
    return results


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=str(Path(__file__).parent / "src" / "captures"))
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()
    capture_all(Path(a.out), only=a.only)
