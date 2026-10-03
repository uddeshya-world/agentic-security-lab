"""Record the README hero GIF: playground level 1 → level 3 (PLAN.md P7.3).

Plays the page with Playwright's video recorder, then converts the webm to an
optimised GIF with ffmpeg (palette pass). Output: docs/media/place-the-control.gif

    python scripts/qa/record_gif.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PAGE = sys.argv[1] if len(sys.argv) > 1 else (ROOT / "lab" / "ui" / "play.html").as_uri()
OUT = ROOT / "docs" / "media" / "place-the-control.gif"
W, H = 1100, 720


def main() -> int:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("ffmpeg not found on PATH")
        return 1
    tmp = Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": W, "height": H}, color_scheme="dark",
                            record_video_dir=str(tmp), record_video_size={"width": W, "height": H})
        page = ctx.new_page()
        page.route("**/fonts.{googleapis,gstatic}.com/**", lambda r: r.abort())
        page.goto(PAGE, wait_until="domcontentloaded")
        page.evaluate("localStorage.clear()")
        page.reload(wait_until="domcontentloaded")
        page.add_style_tag(content=".hero{display:none}")
        page.wait_for_timeout(600)
        # Level 1: step through the six hops
        for _ in range(5):
            page.click("#l1-next")
            page.wait_for_timeout(900)
        page.wait_for_timeout(900)
        # Level 2: pick the two egress controls and run
        page.click("#l1-next")
        page.wait_for_timeout(700)
        page.click("label:has(#ctl-mail)")
        page.wait_for_timeout(400)
        page.click("label:has(#ctl-url)")
        page.wait_for_timeout(400)
        page.click("#l2-run")
        page.wait_for_timeout(500)
        page.evaluate("document.getElementById('l2-result').scrollIntoView({block:'center'})")
        page.wait_for_timeout(1800)
        # Level 3: wrong answer, then the cut
        page.click("#to3")
        page.wait_for_timeout(700)
        page.click("#opts .opt >> nth=0")
        page.wait_for_timeout(1400)
        page.click("#opts .opt >> nth=3")
        page.wait_for_timeout(2200)
        video = page.video.path()
        ctx.close()
        b.close()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    palette = tmp / "palette.png"
    vf = "fps=7,scale=720:-1:flags=lanczos"
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(video), "-vf", f"{vf},palettegen=max_colors=48:stats_mode=diff", str(palette)], check=True)
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(video), "-i", str(palette),
                    "-lavfi", f"{vf}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle", str(OUT)], check=True)
    size = OUT.stat().st_size
    print(f"{OUT} {size / 1e6:.2f} MB")
    return 0 if size <= 4_000_000 else 2


if __name__ == "__main__":
    sys.exit(main())
