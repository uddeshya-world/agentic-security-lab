#!/usr/bin/env python3
"""Build all 9 CyberRange Core explainer videos.

Usage:
  /workspace/video-build/.venv/bin/python docs/video/build.py
  /workspace/video-build/.venv/bin/python docs/video/build.py --only 00-orientation
  /workspace/video-build/.venv/bin/python docs/video/build.py --skip-capture
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
SRC = ROOT / "src"
OUT = ROOT / "out"
SLIDES_DIR = SRC / "slides"
CAPTURES = SRC / "captures"
AUDIO = SRC / "audio"
BEATS_DIR = SRC / "beats"
WORK = ROOT / ".work"

# Ensure we can import sibling modules
sys.path.insert(0, str(ROOT))

VOICE = "bf_emma"
ORDER = [
    "00-orientation",
    "01-tool-abuse-sqli",
    "16-direct-injection",
    "02-rag-poisoning",
    "03-cross-tool-exfil",
    "17-data-guards",
    "18-agent-identity",
    "04-agent-exploit",
    "05-guardrail-map",
]

# Lab UI titles (win over script titles when they differ)
LAB_TITLES = {
    # Exact scenario titles as the lab UI prints them (lab strings win over the script).
    "00-orientation": "What is an agent with tools?",
    "01-tool-abuse-sqli": "Tool abuse — SQL injection (no LLM needed)",
    "16-direct-injection": "Direct prompt injection & jailbreak",
    "02-rag-poisoning": "Poison the LLM context (RAG)",
    "03-cross-tool-exfil": "Cross-tool exfiltration (dump → email)",
    "17-data-guards": "Data guards — DLP for agents",
    "18-agent-identity": "Agent identity & confused deputy",
    "04-agent-exploit": "Exploit the agent (RAG → planner → tools)",
    "05-guardrail-map": "Guardrail map — what to build and where",
}

# Narration deltas vs CORE_VIDEO_SCRIPTS.md (lab UI strings win)
NARRATION_FIXES: dict[str, dict[int, str]] = {
    # beat index -> replacement narration (only where lab wording differs meaningfully)
    # Most script lines already match lab events; keep empty unless needed.
}

# Explicit visual plan per (scenario, beat_index):
#   ("slide", builder_name) or ("capture", capture_id) or ("slide", builder_name, kwargs)
def plan_visuals(scenario: str, beats: list[dict]) -> list[dict]:
    """Return visual plan entries aligned with beats."""
    n = len(beats)
    plans: list[dict] = [{} for _ in range(n)]

    def S(i, name, **kw):
        plans[i] = {"type": "slide", "name": name, "kw": kw}

    # Default push-in per capture kind: run shots zoom to the timeline column (right),
    # lesson shots to the step text (left), area/mailhog get a gentle drift.
    ZOOMS = {
        "vuln-run": {"z": 1.55, "ax": 1.0, "ay": 0.6},
        "secure-run": {"z": 1.55, "ax": 1.0, "ay": 0.6},
        "forensics": {"z": 1.55, "ax": 1.0, "ay": 0.45},
        "run-map": {"z": 1.55, "ax": 1.0, "ay": 0.45},
        "scenario": {"z": 1.6, "ax": 0.3, "ay": 0.2},
        "scenario-map": {"z": 1.6, "ax": 0.3, "ay": 0.2},
        "area": {"z": 1.15, "ax": 0.5, "ay": 0.2},
        "mailhog": {"z": 1.08, "ax": 0.5, "ay": 0.5},
    }

    def C(i, cid, zoom=None):
        plans[i] = {"type": "capture", "id": cid, "zoom": zoom or ZOOMS.get(cid)}

    if scenario == "00-orientation":
        S(0, "office")
        S(1, "office")
        S(2, "office")
        S(3, "office")
        C(4, "area")
        S(5, "map", highlight="EXECUTOR")
        S(6, "break", text=beats[6]["narration"])
        S(7, "end", open_label="Open", title=LAB_TITLES[scenario],
          hint="Confirm your lab is running.")
    elif scenario == "01-tool-abuse-sqli":
        S(0, "library")
        S(1, "library")
        C(2, "scenario")
        C(3, "vuln-run")
        S(4, "sql", sql="SELECT * FROM customers WHERE 1=1", count=3, mode="vulnerable")
        C(5, "secure-run")
        S(6, "break", text=beats[6]["narration"])
        S(7, "end", open_label="Open", title=LAB_TITLES[scenario],
          hint="Run it yourself, then switch to secure.")
    elif scenario == "16-direct-injection":
        S(0, "bank")
        S(1, "bank")
        S(2, "bank")
        C(3, "scenario")
        C(4, "vuln-run")
        C(5, "secure-run")
        S(6, "break", text=beats[6]["narration"])
        S(7, "end", open_label="Open", title=LAB_TITLES[scenario],
          hint="Run both modes and find which part said no.")
    elif scenario == "02-rag-poisoning":
        S(0, "handbook")
        S(1, "handbook")
        C(2, "scenario")
        C(3, "vuln-run")
        C(4, "secure-run")
        S(5, "contained", layer="RAG",
          detail="SECURE_MODE RAG filter dropped trust=untrusted chunks before they entered context\n\nRetrieved 3 chunk(s). Poison instructions present=False")
        S(6, "break", text=beats[6]["narration"])
        S(7, "end", open_label="Open", title=LAB_TITLES[scenario],
          hint="Plant the poison, retrieve it, then quarantine it.")
    elif scenario == "03-cross-tool-exfil":
        S(0, "postroom")
        S(1, "postroom")
        C(2, "scenario")
        C(3, "vuln-run")
        C(4, "mailhog")
        C(5, "secure-run")
        S(6, "break", text=beats[6]["narration"])
        S(7, "end", open_label="Open", title=LAB_TITLES[scenario],
          hint="Watch the export land in MailHog, then prove it cannot.")
    elif scenario == "17-data-guards":
        S(0, "airport")
        S(1, "airport")
        S(2, "airport")
        S(3, "channels")
        C(4, "vuln-run")
        C(5, "secure-run")
        C(6, "forensics")
        S(7, "break", text=beats[7]["narration"])
        S(8, "end", open_label="Open", title=LAB_TITLES[scenario],
          hint="Find which control stopped the SSN.")
    elif scenario == "18-agent-identity":
        S(0, "valet")
        S(1, "valet")
        C(2, "scenario")
        C(3, "vuln-run")
        C(4, "secure-run")
        S(5, "generic", title="Refuse vs scope",
          body_text="SQL injection secure run refused the call. Identity narrows it to the person signed in — one row, Alice’s.")
        S(6, "break", text=beats[6]["narration"])
        S(7, "end", open_label="Open", title=LAB_TITLES[scenario],
          hint="Compare your two runs and see whose rows came back.")
    elif scenario == "04-agent-exploit":
        S(0, "heist")
        C(1, "scenario")
        C(2, "vuln-run")
        S(3, "bank_doors")
        C(4, "secure-run")
        S(5, "generic", title="Later layers hold on their own",
          body_text="The lab still feeds the hijacked plan to the executor. Schema and egress still refuse.")
        S(6, "break", text=beats[6]["narration"])
        S(7, "end", open_label="Open", title=LAB_TITLES[scenario],
          hint="Run the full chain, then make each guardrail name itself.")
    elif scenario == "05-guardrail-map":
        S(0, "fireplan")
        C(1, "scenario")
        S(2, "hops")
        C(3, "run-map")
        S(4, "new_tool")
        S(5, "break", text=beats[5]["narration"])
        S(6, "end", open_label="Finish the Core path",
          title="Claim your completion badge",
          hint="Answer the last question, then claim it on the Area page.")
    else:
        for i, b in enumerate(beats):
            on = b.get("on_screen", "").lower()
            if "analogy breaks" in on:
                S(i, "break", text=b["narration"])
            elif on.startswith("end card"):
                S(i, "end", open_label="Open", title=LAB_TITLES.get(scenario, scenario),
                  hint=b["narration"])
            else:
                S(i, "generic", title=scenario, body_text=b.get("on_screen", ""))
    return plans


def render_slide(name: str, dest_html: Path, dest_png: Path, page, **kw) -> Path:
    import slides as S

    builders = {
        "office": S.slide_office,
        "map": lambda: S.slide_map(kw.get("highlight")),
        "break": lambda: S.slide_break(kw["text"]),
        "end": lambda: S.slide_end(kw.get("open_label", "Open"), kw["title"], kw.get("hint", "")),
        "library": S.slide_library,
        "bank": S.slide_bank,
        "handbook": S.slide_handbook,
        "postroom": S.slide_postroom,
        "airport": S.slide_airport,
        "valet": S.slide_valet,
        "heist": S.slide_heist,
        "bank_doors": S.slide_bank_doors,
        "fireplan": S.slide_fireplan,
        "hops": S.slide_hops,
        "new_tool": S.slide_new_tool,
        "channels": S.slide_channels,
        "contained": lambda: S.slide_contained(kw["layer"], kw["detail"]),
        "sql": lambda: S.slide_sql_block(kw["sql"], kw["count"], kw["mode"]),
        "generic": lambda: S.slide_generic(kw["title"], kw["body_text"], kw.get("kicker", "Beat")),
        "title": lambda: S.slide_title(kw["title"], kw.get("subtitle", ""), kw.get("kicker", "Core explainer")),
    }
    html = builders[name]()
    S.write_html(dest_html, html)
    page.goto(dest_html.as_uri(), wait_until="networkidle")
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.screenshot(path=str(dest_png), full_page=False)
    return dest_png



def beat_min_durations(beats: list[dict], target: float) -> list[float]:
    """Minimum on-screen seconds per beat from script timestamps, scaled to target."""
    def parse(t: str) -> float:
        parts = t.split(":")
        if len(parts) == 2:
            return int(parts[0]) * 60 + float(parts[1])
        return float(parts[0])
    starts = [parse(b["time"]) for b in beats]
    # inferred end = last start + max(8, target - last start)
    end = max(target, starts[-1] + 8.0)
    bounds = starts + [end]
    raw = [max(0.8, bounds[i + 1] - bounds[i]) for i in range(len(beats))]
    # scale so sum(raw) ~= target (scripts sometimes undershoot)
    s = sum(raw)
    if s > 0 and abs(s - target) > 1.0:
        raw = [d * (target / s) for d in raw]
    return raw

def load_scripts() -> list[dict]:
    data = json.loads((SRC / "scripts.json").read_text(encoding="utf-8"))
    by_id = {v["scenario"]: v for v in data["videos"]}
    ordered = []
    for sid in ORDER:
        v = by_id[sid]
        # apply narration fixes
        fixes = NARRATION_FIXES.get(sid, {})
        beats = []
        for i, b in enumerate(v["beats"]):
            nb = dict(b)
            if i in fixes:
                nb["narration_original"] = b["narration"]
                nb["narration"] = fixes[i]
            beats.append(nb)
        v = dict(v)
        v["beats"] = beats
        v["filename"] = sid
        ordered.append(v)
    return ordered


def ensure_dirs():
    for d in (OUT, SLIDES_DIR, CAPTURES, AUDIO, BEATS_DIR, WORK):
        d.mkdir(parents=True, exist_ok=True)


def synthesize_all(videos: list[dict], speed: float = 1.0) -> None:
    import tts as T
    for v in videos:
        sid = v["filename"]
        adir = AUDIO / sid
        adir.mkdir(parents=True, exist_ok=True)
        meta = []
        print(f"[tts] {sid}", flush=True)
        for i, b in enumerate(v["beats"]):
            wav = adir / f"beat-{i:02d}.wav"
            if wav.exists() and wav.stat().st_size > 1000:
                dur = T.wav_duration(wav)
                print(f"  reuse beat-{i:02d} ({dur:.2f}s)", flush=True)
            else:
                dur = T.synthesize(b["narration"], wav, speed=speed)
                print(f"  beat-{i:02d} ({dur:.2f}s)", flush=True)
            meta.append({"index": i, "duration": dur, "path": str(wav), "text": b["narration"]})
        (adir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def render_all_slides(videos: list[dict]) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080}, color_scheme="dark")
        for v in videos:
            sid = v["filename"]
            plans = plan_visuals(sid, v["beats"])
            sdir = SLIDES_DIR / sid
            sdir.mkdir(parents=True, exist_ok=True)
            print(f"[slides] {sid}", flush=True)
            import slides as SL
            num = ORDER.index(sid) + 1
            th_html = sdir / "thumb.html"
            SL.write_html(th_html, SL.slide_thumb(num, LAB_TITLES[sid], v["one_idea"][0].upper() + v["one_idea"][1:]))
            page.goto(th_html.as_uri(), wait_until="networkidle")
            page.screenshot(path=str(sdir / "thumb.png"))
            for i, (b, plan) in enumerate(zip(v["beats"], plans)):
                if plan.get("type") != "slide":
                    continue
                html_path = sdir / f"beat-{i:02d}.html"
                png_path = sdir / f"beat-{i:02d}.png"
                render_slide(plan["name"], html_path, png_path, page, **plan.get("kw", {}))
                print(f"  slide beat-{i:02d} ({plan['name']})", flush=True)
        browser.close()


def resolve_frame(sid: str, i: int, plan: dict) -> Path:
    if plan["type"] == "slide":
        return SLIDES_DIR / sid / f"beat-{i:02d}.png"
    cid = plan["id"]
    path = CAPTURES / sid / f"{cid}.png"
    if not path.exists():
        # fallback to a slide if capture missing
        alt = SLIDES_DIR / sid / f"beat-{i:02d}.png"
        if alt.exists():
            return alt
        raise FileNotFoundError(path)
    return path


def compose_video(v: dict) -> dict:
    import compose as C
    import tts as T

    sid = v["filename"]
    plans = plan_visuals(sid, v["beats"])
    meta = json.loads((AUDIO / sid / "meta.json").read_text(encoding="utf-8"))
    wdir = WORK / sid
    if wdir.exists():
        shutil.rmtree(wdir)
    wdir.mkdir(parents=True)

    clips = []
    srt_beats = []
    t = 0.0
    gap = 0.12
    print(f"[compose] {sid}", flush=True)
    mins = beat_min_durations(v["beats"], float(v["target_duration_s"]))
    for i, (b, plan, m) in enumerate(zip(v["beats"], plans, meta)):
        frame = resolve_frame(sid, i, plan)
        wav = Path(m["path"])
        clip = wdir / f"clip-{i:02d}.mp4"
        # Hold frame at least as long as script beat; never shorter than audio
        min_d = max(mins[i], m["duration"] + 0.15)
        C.still_clip(frame, wav, clip, min_duration=min_d, zoom=plan.get("zoom") if plan["type"] == "capture" else None)
        dur = C.probe_duration(clip)
        # Captions track spoken audio, not the silent hold
        srt_beats.append({"start": t, "end": t + m["duration"], "text": b["narration"]})
        t += dur
        clips.append(clip)
        print(f"  clip-{i:02d} {dur:.2f}s (audio {m['duration']:.2f}s) <- {plan['type']}:{plan.get('name') or plan.get('id')}", flush=True)

    raw = wdir / "raw.mp4"
    C.concat_clips(clips, raw)

    srt_path = OUT / f"{sid}.srt"
    C.write_srt(srt_beats, srt_path)

    final = OUT / f"{sid}.mp4"
    try:
        ass_path = SRC / "captions" / f"{sid}.ass"
        C.write_ass(srt_beats, ass_path)
        C.burn_captions(raw, ass_path, final)
    except Exception as e:
        print(f"  caption burn failed ({e}); copying raw", flush=True)
        shutil.copy(raw, final)

    thumb = OUT / f"{sid}-thumb.png"
    poster = SLIDES_DIR / sid / "thumb.png"
    if poster.exists():
        import subprocess
        subprocess.check_call(["ffmpeg", "-y", "-i", str(poster), "-vf", "scale=1280:720", str(thumb)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        C.make_thumb(final, thumb, t=min(2.0, max(0.5, t * 0.15)))

    # contact sheet of beat frames
    frames = [resolve_frame(sid, i, plans[i]) for i in range(len(plans))]
    sheet = OUT / f"{sid}-contact.png"
    try:
        C.contact_sheet(frames, sheet, cols=3)
    except Exception as e:
        print(f"  contact sheet skip: {e}", flush=True)
        sheet = None

    duration = C.probe_duration(final)
    size = final.stat().st_size
    # Save beat plan
    plan_out = {
        "scenario": sid,
        "title": v["title"],
        "target_duration_s": v["target_duration_s"],
        "actual_duration_s": duration,
        "voice": VOICE,
        "beats": [
            {
                "index": i,
                "narration": v["beats"][i]["narration"],
                "on_screen": v["beats"][i]["on_screen"],
                "visual": plans[i],
                "audio_s": meta[i]["duration"],
            }
            for i in range(len(v["beats"]))
        ],
    }
    (BEATS_DIR / f"{sid}.json").write_text(json.dumps(plan_out, indent=2), encoding="utf-8")

    return {
        "filename": f"{sid}.mp4",
        "duration": duration,
        "size": size,
        "path": str(final),
        "srt": str(srt_path),
        "thumb": str(thumb),
        "contact": str(sheet) if sheet else None,
        "target": v["target_duration_s"],
    }


def speed_for_target(v: dict, meta_durations: list[float]) -> float:
    """If total narration is far from target, nudge TTS speed."""
    total = sum(meta_durations)
    target = float(v["target_duration_s"])
    # leave ~4% for gaps/ends
    ideal = target * 0.96
    if total <= 0:
        return 1.0
    ratio = total / ideal
    # clamp speed 0.92 .. 1.12
    if 0.92 <= ratio <= 1.08:
        return 1.0
    speed = max(0.92, min(1.12, ratio))
    return speed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--skip-capture", action="store_true")
    ap.add_argument("--skip-tts", action="store_true")
    ap.add_argument("--skip-slides", action="store_true")
    ap.add_argument("--skip-compose", action="store_true")
    ap.add_argument("--speed", type=float, default=1.0, help="base TTS speed")
    args = ap.parse_args()

    ensure_dirs()
    videos = load_scripts()
    if args.only:
        videos = [v for v in videos if v["filename"] in args.only]

    # Write narration text files for rebuildability
    for v in videos:
        ndir = SRC / "narration" / v["filename"]
        ndir.mkdir(parents=True, exist_ok=True)
        for i, b in enumerate(v["beats"]):
            (ndir / f"beat-{i:02d}.txt").write_text(b["narration"] + "\n", encoding="utf-8")
        (ndir / "full.txt").write_text(
            "\n\n".join(b["narration"] for b in v["beats"]) + "\n", encoding="utf-8"
        )

    t0 = time.time()

    if not args.skip_tts:
        synthesize_all(videos, speed=args.speed)

    if not args.skip_slides:
        render_all_slides(videos)

    if not args.skip_capture:
        import capture as Cap
        Cap.capture_all(CAPTURES, only=[v["filename"] for v in videos])

    results = []
    if not args.skip_compose:
        for v in videos:
            results.append(compose_video(v))

    report = {
        "voice": VOICE,
        "engine": "Kokoro-82M",
        "lufs_target": -16,
        "videos": results,
        "elapsed_s": round(time.time() - t0, 1),
    }
    (OUT / "build-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\n=== BUILD REPORT ===")
    for r in results:
        mb = r["size"] / (1024 * 1024)
        flag = "OK" if 65 <= r["duration"] <= 110 else "CHECK"
        print(f"{r['filename']:28s} {r['duration']:6.1f}s  (target {r['target']})  {mb:5.1f} MiB  [{flag}]")
    print(f"elapsed {report['elapsed_s']}s  voice={VOICE}")


if __name__ == "__main__":
    # Re-exec under video-build venv if needed
    venv_py = Path("/workspace/video-build/.venv/bin/python")
    if venv_py.exists() and Path(sys.executable).resolve() != venv_py.resolve():
        os.execv(str(venv_py), [str(venv_py), *sys.argv])
    main()
