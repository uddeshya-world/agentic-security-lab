#!/usr/bin/env python3
"""Synthetic slide generator matching CyberRange dark-theme tokens."""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
WIDTH, HEIGHT = 1920, 1080

# Slides reuse the lab's CSS tokens (copied into assets/).
BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Archivo:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --void:#0a0c10; --plate:#12161c; --shelf:#171c24; --raise:#1d232c;
  --edge:#232a34; --edge-hi:#364150;
  --chalk:#e9ecf1; --ash:#8b94a3; --dim:#7e8796; --prose:#d3d9e2;
  --ember:#ff6b35; --ember-ink:#ffb598; --ember-bed:#341409; --ember-line:#5e2a14;
  --halon:#35e0c0; --halon-ink:#8ff0dd; --halon-bed:#072a24; --halon-line:#125045;
  --brass:#e8b84b; --brass-ink:#f0dda8; --brass-bed:#2b2210;
  --plan:#b79cff; --sunk:#080a0e;
  --display:"Space Grotesk",ui-sans-serif,system-ui,sans-serif;
  --body:"Archivo",ui-sans-serif,system-ui,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;overflow:hidden;background:var(--void);color:var(--chalk);
  font-family:var(--body);-webkit-font-smoothing:antialiased}
body{background:
  radial-gradient(1200px 600px at 10% -10%, rgba(255,107,53,.08), transparent 60%),
  radial-gradient(900px 500px at 110% 110%, rgba(53,224,192,.06), transparent 55%),
  var(--void)}
.frame{position:relative;width:100%;height:100%;padding:64px 80px;display:flex;flex-direction:column}
.top{display:flex;align-items:center;gap:16px;margin-bottom:36px}
.mark{width:36px;height:36px;border-radius:6px;background:linear-gradient(135deg,var(--ember),#c43a12);
  display:grid;place-items:center;font:700 14px/1 var(--display);color:var(--void)}
.brand{font:600 18px/1 var(--display);letter-spacing:.04em;color:var(--ash)}
.kicker{margin-left:auto;font:500 13px/1 var(--mono);color:var(--ember-ink);
  border:1px solid var(--ember-line);background:var(--ember-bed);padding:8px 14px;border-radius:999px;
  text-transform:uppercase;letter-spacing:.08em}
.kicker.halon{color:var(--halon-ink);border-color:var(--halon-line);background:var(--halon-bed)}
.kicker.brass{color:var(--brass-ink);border-color:var(--brass-line);background:var(--brass-bed)}
.stage{flex:1;display:flex;flex-direction:column;justify-content:center;gap:28px;min-height:0}
.title{font:700 56px/1.1 var(--display);color:var(--chalk);max-width:1500px}
.subtitle{font:500 28px/1.35 var(--body);color:var(--prose);max-width:1400px}
.panel{background:var(--plate);border:1px solid var(--edge);border-radius:14px;padding:36px 40px;
  box-shadow:0 20px 60px rgba(0,0,0,.45)}
.panel.sunk{background:var(--sunk)}
.row{display:flex;gap:24px;align-items:stretch}
.card{flex:1;background:var(--shelf);border:1px solid var(--edge);border-radius:12px;padding:28px 30px;
  display:flex;flex-direction:column;gap:14px}
.card h3{font:600 22px/1.2 var(--display);color:var(--chalk)}
.card p,.card li{font:400 20px/1.45 var(--body);color:var(--prose)}
.card .tag{align-self:flex-start;font:500 12px/1 var(--mono);color:var(--ash);
  border:1px solid var(--edge-hi);padding:6px 10px;border-radius:999px;letter-spacing:.06em;text-transform:uppercase}
.card.ember{border-color:var(--ember-line);background:linear-gradient(180deg,var(--ember-bed),var(--shelf))}
.card.halon{border-color:var(--halon-line);background:linear-gradient(180deg,var(--halon-bed),var(--shelf))}
.card.brass{border-color:var(--brass-line);background:linear-gradient(180deg,var(--brass-bed),var(--shelf))}
.mono{font-family:var(--mono);color:var(--halon-ink);font-size:22px;line-height:1.5;white-space:pre-wrap}
.footer{margin-top:auto;display:flex;justify-content:space-between;align-items:center;padding-top:24px;
  border-top:1px solid var(--edge);color:var(--dim);font:500 16px/1 var(--mono)}
.pill{display:inline-flex;align-items:center;gap:8px;padding:10px 16px;border-radius:999px;
  font:600 16px/1 var(--display);border:1px solid var(--edge)}
.pill.ember{background:var(--ember-bed);border-color:var(--ember-line);color:var(--ember-ink)}
.pill.halon{background:var(--halon-bed);border-color:var(--halon-line);color:var(--halon-ink)}
.diagram{display:flex;align-items:center;gap:12px;flex-wrap:wrap;justify-content:center;padding:20px 0}
.node{padding:16px 22px;border-radius:10px;background:var(--raise);border:1px solid var(--edge-hi);
  font:600 18px/1 var(--display);color:var(--chalk);min-width:120px;text-align:center}
.node.hot{border-color:var(--ember);box-shadow:0 0 0 2px rgba(255,107,53,.25);color:var(--ember-ink)}
.node.ok{border-color:var(--halon);color:var(--halon-ink)}
.arrow{color:var(--ash);font:700 24px/1 var(--display)}
.break-box{border:1px solid var(--brass-line);background:linear-gradient(180deg,var(--brass-bed),var(--plate));
  border-radius:14px;padding:40px 44px;max-width:1500px}
.break-box .lbl{font:600 14px/1 var(--mono);color:var(--brass);letter-spacing:.12em;text-transform:uppercase;margin-bottom:18px}
.break-box .body{font:500 32px/1.4 var(--body);color:var(--chalk)}
.end-card{text-align:left}
.end-card .open{font:600 18px/1 var(--mono);color:var(--ember);letter-spacing:.1em;text-transform:uppercase;margin-bottom:18px}
.end-card h1{font:700 64px/1.05 var(--display);margin-bottom:24px}
.end-card p{font:500 26px/1.4 var(--body);color:var(--prose);max-width:1200px}
.caption-bar{position:absolute;left:80px;right:80px;bottom:56px;background:rgba(8,10,14,.88);
  border:1px solid var(--edge);border-radius:10px;padding:18px 24px;font:500 22px/1.35 var(--body);color:var(--chalk)}
.list{list-style:none;display:flex;flex-direction:column;gap:14px}
.list li{display:flex;gap:16px;align-items:flex-start;font:500 24px/1.35 var(--body);color:var(--prose)}
.list li::before{content:"";width:10px;height:10px;margin-top:10px;border-radius:50%;background:var(--ember);flex:none}
"""


def _esc(s: str) -> str:
    return html.escape(s, quote=True)


def wrap(body: str, kicker: str = "", kicker_class: str = "", footer_left: str = "", footer_right: str = "") -> str:
    kick = f'<div class="kicker {kicker_class}">{_esc(kicker)}</div>' if kicker else ""
    foot = ""
    if footer_left or footer_right:
        foot = f'<div class="footer"><span>{_esc(footer_left)}</span><span>{_esc(footer_right)}</span></div>'
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark"><head><meta charset="utf-8"/>
<style>{BASE_CSS}</style></head>
<body><div class="frame">
  <div class="top"><div class="mark">CR</div><div class="brand">CyberRange · Core path</div>{kick}</div>
  <div class="stage">{body}</div>
  {foot}
</div></body></html>"""


def slide_title(title: str, subtitle: str, kicker: str = "Core explainer") -> str:
    return wrap(
        f'<div class="title">{_esc(title)}</div><div class="subtitle">{_esc(subtitle)}</div>',
        kicker=kicker,
    )


def slide_analogy(title: str, points: list[str], kicker: str = "Analogy") -> str:
    cards = []
    for i, p in enumerate(points[:3]):
        cls = ["ember", "halon", "brass"][i % 3]
        cards.append(f'<div class="card {cls}"><span class="tag">Beat {i+1}</span><p>{_esc(p)}</p></div>')
    body = f'<div class="title" style="font-size:40px">{_esc(title)}</div><div class="row">{"".join(cards)}</div>'
    return wrap(body, kicker=kicker, kicker_class="")


def slide_office() -> str:
    body = """
    <div class="title" style="font-size:44px">An office with two people</div>
    <div class="row">
      <div class="card ember"><span class="tag">Planner</span><h3>The assistant</h3>
        <p>Reads every letter. Writes sticky-note instructions.</p></div>
      <div class="card halon"><span class="tag">Executor</span><h3>The clerk</h3>
        <p>Holds the keys. Does whatever the note says.</p></div>
      <div class="card brass"><span class="tag">World</span><h3>Cabinet &amp; post</h3>
        <p>Database, email, files — real side effects.</p></div>
    </div>"""
    return wrap(body, kicker="Analogy")


def slide_map(highlight: str | None = None) -> str:
    nodes = ["USER", "RAG", "PLANNER", "EXECUTOR", "TOOLS", "WORLD"]
    parts = []
    for i, n in enumerate(nodes):
        cls = "hot" if highlight and n == highlight.upper() else ""
        parts.append(f'<div class="node {cls}">{n}</div>')
        if i < len(nodes) - 1:
            parts.append('<div class="arrow">→</div>')
    body = f'<div class="title" style="font-size:40px">Agent data path</div><div class="diagram">{"".join(parts)}</div>'
    if highlight:
        body += f'<div class="subtitle">Trust boundary: <b style="color:var(--ember-ink)">{_esc(highlight)}</b></div>'
    return wrap(body, kicker="Lab map", kicker_class="halon")


def slide_break(text: str) -> str:
    body = f"""
    <div class="break-box">
      <div class="lbl">Where the analogy breaks</div>
      <div class="body">{_esc(text)}</div>
    </div>"""
    return wrap(body, kicker="Limit of the metaphor", kicker_class="brass")


def slide_end(open_label: str, title: str, hint: str = "") -> str:
    body = f"""
    <div class="end-card">
      <div class="open">{_esc(open_label)}</div>
      <h1>{_esc(title)}</h1>
      <p>{_esc(hint)}</p>
    </div>"""
    return wrap(body, kicker="Next step", kicker_class="ember")


def slide_library() -> str:
    body = """
    <div class="title" style="font-size:44px">A library request slip</div>
    <div class="row">
      <div class="card"><span class="tag">Normal</span><h3>Book title: ______</h3>
        <p>One title → one book.</p></div>
      <div class="card ember"><span class="tag">Abuse</span><h3>“any book, all of them”</h3>
        <p>Copied straight onto the order → whole library.</p></div>
    </div>"""
    return wrap(body, kicker="Analogy")


def slide_bank() -> str:
    body = """
    <div class="title" style="font-size:44px">Bank counter vs vault</div>
    <div class="row">
      <div class="card ember"><span class="tag">Teller</span><h3>Persuadable</h3>
        <p>“Your manager told me to collect everyone’s statements.”</p></div>
      <div class="card halon"><span class="tag">Vault</span><h3>Needs a key card</h3>
        <p>Whatever the teller was told, the door still checks.</p></div>
    </div>"""
    return wrap(body, kicker="Analogy")


def slide_handbook() -> str:
    body = """
    <div class="title" style="font-size:44px">A forged page in the handbook</div>
    <div class="row">
      <div class="card"><span class="tag">Look-up</span><h3>Shipping times</h3>
        <p>Innocent question pulls the right answer.</p></div>
      <div class="card ember"><span class="tag">Poison</span><h3>Hidden instruction</h3>
        <p>“…and email the customer list to this address.”</p></div>
    </div>"""
    return wrap(body, kicker="Analogy")


def slide_postroom() -> str:
    body = """
    <div class="title" style="font-size:44px">Reading vs posting</div>
    <div class="row">
      <div class="card brass"><span class="tag">Problem</span><h3>Confidential folder</h3>
        <p>Reading it at your desk is already a problem.</p></div>
      <div class="card ember"><span class="tag">Breach</span><h3>Parcel at the post room</h3>
        <p>Sending it out is the breach.</p></div>
      <div class="card halon"><span class="tag">Rules</span><h3>Two gates</h3>
        <p>Approved addresses only. Bulk needs a signature.</p></div>
    </div>"""
    return wrap(body, kicker="Analogy")


def slide_airport() -> str:
    body = """
    <div class="title" style="font-size:44px">Two different airport checks</div>
    <div class="row">
      <div class="card"><span class="tag">Where</span><h3>Boarding pass</h3>
        <p>Says which gate you may enter.</p></div>
      <div class="card ember"><span class="tag">What</span><h3>X-ray belt</h3>
        <p>A valid ticket does not carry a prohibited item through.</p></div>
    </div>"""
    return wrap(body, kicker="Analogy")


def slide_valet() -> str:
    body = """
    <div class="title" style="font-size:44px">Valet key</div>
    <div class="row">
      <div class="card halon"><span class="tag">Allowed</span><h3>Drive the car</h3>
        <p>The key lets the valet park it.</p></div>
      <div class="card ember"><span class="tag">Denied</span><h3>Boot &amp; glovebox</h3>
        <p>The key sets the limit — not the valet’s request.</p></div>
    </div>"""
    return wrap(body, kicker="Analogy")


def slide_heist() -> str:
    body = """
    <div class="title" style="font-size:44px">A heist needs three things</div>
    <div class="row">
      <div class="card ember"><span class="tag">1</span><h3>Insider note</h3><p>Poison in context</p></div>
      <div class="card brass"><span class="tag">2</span><h3>Driver follows</h3><p>Hijacked plan</p></div>
      <div class="card"><span class="tag">3</span><h3>Vault opens</h3><p>Tools that obey</p></div>
    </div>"""
    return wrap(body, kicker="Analogy")


def slide_bank_doors() -> str:
    body = """
    <div class="title" style="font-size:44px">Several doors, each with its own key</div>
    <div class="diagram">
      <div class="node ok">RAG filter</div><div class="arrow">·</div>
      <div class="node ok">Schema</div><div class="arrow">·</div>
      <div class="node ok">Identity</div><div class="arrow">·</div>
      <div class="node ok">Egress</div>
    </div>
    <div class="subtitle">Defense in depth: one failure is not a breach.</div>"""
    return wrap(body, kicker="Defense in depth", kicker_class="halon")


def slide_fireplan() -> str:
    body = """
    <div class="title" style="font-size:44px">A fire plan puts controls on the route</div>
    <div class="subtitle">Not every extinguisher in the lobby — one at each hop on the escape path.</div>
    <div class="diagram" style="margin-top:20px">
      <div class="node">USER</div><div class="arrow">→</div>
      <div class="node">RAG</div><div class="arrow">→</div>
      <div class="node">PLANNER</div><div class="arrow">→</div>
      <div class="node hot">EXECUTOR</div><div class="arrow">→</div>
      <div class="node">TOOLS</div><div class="arrow">→</div>
      <div class="node">WORLD</div>
    </div>"""
    return wrap(body, kicker="Analogy")


def slide_hops() -> str:
    # Layer names exactly as the lab prints them in the guardrail map (g1 evidence).
    items = [
        "1. Input DLP",
        "2. Context / RAG + context DLP",
        "3. Planner (LLM) output",
        "4. Identity / principal",
        "5. Schema / args",
        "6. Least privilege",
        "7. Tool DLP + HITL + egress",
        "8. Output DLP",
    ]
    cells = "".join(
        f'<div class="card" style="flex:0 0 calc(25% - 18px);padding:22px 24px"><h3 style="font-size:22px">{_esc(i)}</h3></div>'
        for i in items)
    body = (f'<div class="title" style="font-size:40px">Eight hops, a control on each</div>'
            f'<div class="row" style="flex-wrap:wrap">{cells}</div>')
    return wrap(body, kicker="Guardrail map", kicker_class="halon")


def slide_new_tool() -> str:
    body = """
    <div class="title" style="font-size:44px">When a new tool arrives</div>
    <div class="panel">
      <div class="mono">save report → partner folder</div>
      <p style="margin-top:24px;font:500 26px/1.4 var(--body);color:var(--prose)">
        Place it on the map. Does it bring data in, or let data out?
      </p>
    </div>"""
    return wrap(body, kicker="Design question", kicker_class="brass")


def slide_channels() -> str:
    body = """
    <div class="title" style="font-size:40px">Four data channels</div>
    <div class="row">
      <div class="card ember"><span class="tag">1</span><h3>Prompt</h3><p>User input</p></div>
      <div class="card"><span class="tag">2</span><h3>Retrieved chunk</h3><p>RAG context</p></div>
      <div class="card brass"><span class="tag">3</span><h3>Tool result</h3><p>Side-effect payload</p></div>
      <div class="card halon"><span class="tag">4</span><h3>Model answer</h3><p>Output</p></div>
    </div>"""
    return wrap(body, kicker="Data guards")


def slide_generic(title: str, body_text: str, kicker: str = "Beat") -> str:
    body = f'<div class="title" style="font-size:42px">{_esc(title)}</div><div class="panel"><p style="font:500 26px/1.45 var(--body);color:var(--prose)">{_esc(body_text)}</p></div>'
    return wrap(body, kicker=kicker)


def slide_contained(layer: str, detail: str) -> str:
    body = f"""
    <div class="title" style="font-size:40px">Contained at <span style="color:var(--halon-ink)">{_esc(layer)}</span></div>
    <div class="panel sunk"><div class="mono">{_esc(detail)}</div></div>
    <div class="pill halon" style="align-self:flex-start;margin-top:8px">DEFENSE held</div>"""
    return wrap(body, kicker="Secure mode", kicker_class="halon")


def slide_sql_block(sql: str, count: int, mode: str) -> str:
    body = f"""
    <div class="title" style="font-size:40px">What the tool built</div>
    <div class="panel sunk"><div class="mono">{_esc(sql)}</div></div>
    <div class="row" style="margin-top:8px">
      <div class="pill ember">count={count}</div>
      <div class="pill">mode={_esc(mode)}</div>
    </div>"""
    return wrap(body, kicker="Timeline", kicker_class="ember")


# Per-video beat → slide HTML factory (for synthetic beats).
# Lab beats are filled by capture frames; these cover analogy/break/end/diagram.

SLIDE_BUILDERS = {
    # keys: (scenario, beat_index) — filled by build.py via heuristics + explicit map
}


def write_html(path: Path, html_str: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_str, encoding="utf-8")
    return path


def slide_thumb(number: int, title: str, idea: str) -> str:
    """1920x1080 poster; downscaled to 1280x720 for the thumbnail."""
    return f"""<!DOCTYPE html><html data-theme="dark"><head><meta charset="utf-8"/>
<style>{BASE_CSS}
.t-wrap{{position:relative;width:1920px;height:1080px;padding:96px 112px;display:flex;flex-direction:column}}
.t-num{{font:700 220px/0.9 var(--display);color:var(--ember);letter-spacing:-.04em}}
.t-title{{font:700 96px/1.02 var(--display);color:var(--chalk);max-width:1600px;margin-top:24px}}
.t-idea{{font:500 34px/1.35 var(--body);color:var(--prose);max-width:1450px;margin-top:32px}}
.t-bar{{position:absolute;left:0;right:0;bottom:0;height:14px;background:linear-gradient(90deg,var(--ember),var(--brass),var(--halon))}}
</style></head><body><div class="t-wrap">
  <div class="top"><div class="mark">CR</div><div class="brand">CyberRange · Core path</div>
    <div class="kicker">Explainer {number} of 9</div></div>
  <div class="t-num">{number:02d}</div>
  <div class="t-title">{_esc(title)}</div>
  <div class="t-idea">{_esc(idea)}</div>
  <div class="t-bar"></div>
</div></body></html>"""
