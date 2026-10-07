"""Core explainer videos: every Core lesson has one, and the pieces agree.

The MP4s live in the `videos-v1` release and are served by GitHub Pages, so this
test never downloads them. It checks what ships in git: the scenario entries, the
transcripts and posters the lab serves offline, the player wiring, and the Pages
workflow that publishes the files. No Docker needed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCEN = ROOT / "content" / "areas" / "ai-security" / "scenarios"
VIDEO = ROOT / "lab" / "ui" / "video"
CORE = [
    "00-orientation", "01-tool-abuse-sqli", "16-direct-injection", "02-rag-poisoning",
    "03-cross-tool-exfil", "17-data-guards", "18-agent-identity", "04-agent-exploit",
    "05-guardrail-map",
]
CUE = re.compile(r"(\d\d):(\d\d):(\d\d)\.(\d\d\d) --> (\d\d):(\d\d):(\d\d)\.(\d\d\d)")


def _secs(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def test_every_core_scenario_has_a_video():
    for sid in CORE:
        v = json.loads((SCEN / sid / "scenario.json").read_text(encoding="utf-8")).get("video")
        assert v and v["src"] == sid, sid
        assert 60 <= v["seconds"] <= 100, sid


def test_transcripts_and_posters_ship_with_the_lab():
    for sid in CORE:
        seconds = json.loads((SCEN / sid / "scenario.json").read_text(encoding="utf-8"))["video"]["seconds"]
        vtt = (VIDEO / f"{sid}.vtt").read_text(encoding="utf-8")
        assert vtt.startswith("WEBVTT"), sid
        ends = [_secs(*m.groups()[4:]) for m in CUE.finditer(vtt)]
        assert len(ends) >= 5, sid
        assert ends[-1] <= seconds + 1, f"{sid}: captions run past the video"
        assert "certif" not in vtt.lower(), sid
        assert (VIDEO / f"{sid}.jpg").stat().st_size < 120_000, sid


def test_payload_passes_the_video_through():
    from lab import content

    content._load_all.cache_clear()
    p = content.scenario_payload("ai-security", "01-tool-abuse-sqli")
    assert p["video"] == {"src": "01-tool-abuse-sqli", "seconds": 85}
    assert content.scenario_payload("ai-security", "19-mcp-tool-poisoning")["video"] is None


def test_player_streams_from_pages_and_never_autoplays():
    js = (ROOT / "lab" / "ui" / "cyberrange.js").read_text(encoding="utf-8")
    assert 'VIDEO_BASE = "https://uddeshya-world.github.io/agentic-security-lab/video/"' in js
    assert "autoplay" not in js
    assert 'preload="metadata"' in js
    html = (ROOT / "lab" / "ui" / "scenario.html").read_text(encoding="utf-8")
    assert "CR.videoButton(data.video)" in html


def test_pages_publishes_the_release_videos():
    wf = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    assert "VIDEO_RELEASE: videos-v1" in wf
    assert 'gh release download "$VIDEO_RELEASE"' in wf
    assert "-name '*.mp4' | wc -l)\" -eq 9" in wf


def test_videos_stay_out_of_git():
    tracked = [p for p in ROOT.rglob("*.mp4") if ".git" not in p.parts and "out" not in p.parts]
    assert not tracked, tracked
