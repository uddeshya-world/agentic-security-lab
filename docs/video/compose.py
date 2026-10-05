#!/usr/bin/env python3
"""Compose one explainer video from beat images + narration WAVs + SRT."""
from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path


def split_cues(text: str, max_chars: int = 96) -> list[str]:
    """Split narration into caption cues of at most two ~48-char lines."""
    import re
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    cues: list[str] = []
    for s in sentences:
        if len(s) <= max_chars:
            cues.append(s)
            continue
        # break long sentences at commas/colons, then by words
        parts = re.split(r"(?<=[,:;])\s+", s)
        buf = ""
        for p in parts:
            if len(buf) + len(p) + 1 <= max_chars:
                buf = f"{buf} {p}".strip()
            else:
                if buf:
                    cues.append(buf)
                while len(p) > max_chars:
                    cut = p.rfind(" ", 0, max_chars)
                    cut = cut if cut > 0 else max_chars
                    cues.append(p[:cut]); p = p[cut:].strip()
                buf = p
        if buf:
            cues.append(buf)
    # merge tiny trailing cues
    merged: list[str] = []
    for c in cues:
        if merged and len(c) < 18 and len(merged[-1]) + len(c) + 1 <= max_chars:
            merged[-1] = f"{merged[-1]} {c}"
        else:
            merged.append(c)
    return merged


def timed_cues(beats: list[dict]) -> list[tuple[float, float, str]]:
    out = []
    for b in beats:
        cues = split_cues(b["text"])
        total = sum(len(c) for c in cues) or 1
        t = b["start"]
        span = b["end"] - b["start"]
        for c in cues:
            d = span * len(c) / total
            out.append((t, t + d - 0.04, c))
            t += d
    return out


def write_srt(beats: list[dict], path: Path) -> Path:
    """beats: [{start, end, text}] in seconds. Long beats become several cues, timed by length."""
    lines = []
    for n, (a, z, c) in enumerate(timed_cues(beats), 1):
        lines += [str(n), f"{_ts(a)} --> {_ts(z)}", textwrap.fill(c, width=50), ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _ass_ts(s: float) -> str:
    s = max(0.0, s)
    h = int(s // 3600); m = int((s % 3600) // 60); sec = s - h * 3600 - m * 60
    return f"{h}:{m:02d}:{sec:05.2f}"


def write_ass(beats: list[dict], path: Path) -> Path:
    """Burn-in captions at native 1080p, styled with CyberRange tokens (chalk on void)."""
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Archivo,44,&H00F1ECE9,&H00F1ECE9,&H1E100C0A,&H1E100C0A,0,0,0,0,100,100,0,0,3,14,0,2,160,160,64,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for a, z, c in timed_cues(beats):
        txt = textwrap.fill(c, width=52).replace("\n", "\\N")
        ev.append(f"Dialogue: 0,{_ass_ts(a)},{_ass_ts(z)},Cap,,0,0,0,,{txt}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header + "\n".join(ev) + "\n", encoding="utf-8")
    return path


def _ts(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms == 1000:
        s += 1
        ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def still_clip(image: Path, audio: Path, out: Path, fps: int = 30, min_duration: float | None = None,
               zoom: dict | None = None) -> Path:
    """H.264 clip of a still image, held for max(audio, min_duration).

    zoom: optional {"z": max_zoom, "ax": 0..1, "ay": 0..1} — eased push-in toward an anchor
    (ax=1 means the right edge). Source images can be 2x (3840x2160) for crisp zooms.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio)],
        capture_output=True, text=True, check=True,
    )
    aud = float(r.stdout.strip())
    dur = max(aud, float(min_duration or 0), 0.5)
    pad = max(0.0, dur - aud + 0.05)
    frames = int(round(dur * fps))
    if zoom and zoom.get("z", 1.0) > 1.001:
        zmax = float(zoom["z"]); ax = float(zoom.get("ax", 0.5)); ay = float(zoom.get("ay", 0.5))
        ramp = max(1, int(frames * 0.55))
        p = f"min(on/{ramp},1)"
        ease = f"({p})*({p})*(3-2*({p}))"
        vf = (
            "scale=3840:2160:force_original_aspect_ratio=decrease,pad=3840:2160:(ow-iw)/2:(oh-ih)/2,setsar=1,"
            f"zoompan=z='1+({zmax}-1)*{ease}':x='(iw-iw/zoom)*{ax}':y='(ih-ih/zoom)*{ay}'"
            f":d={frames}:s=1920x1080:fps={fps},format=yuv420p"
        )
        vin = ["-i", str(image)]
    else:
        vf = ("scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
              "setsar=1,format=yuv420p")
        vin = ["-loop", "1", "-framerate", str(fps), "-t", f"{dur:.3f}", "-i", str(image)]
    cmd = [
        "ffmpeg", "-y", *vin, "-i", str(audio),
        "-filter_complex", f"[1:a]apad=pad_dur={pad:.3f}[a];[0:v]{vf}[v]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-r", str(fps), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", f"{dur:.3f}", "-movflags", "+faststart", str(out),
    ]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


def concat_clips(clips: list[Path], out: Path) -> Path:
    lst = out.with_suffix(".txt")
    lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips), encoding="utf-8")
    subprocess.check_call(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return out


def burn_captions(video: Path, ass: Path, out: Path) -> Path:
    ass_esc = str(ass.resolve()).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(video), "-vf", f"ass={ass_esc}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30",
         "-c:a", "copy", "-movflags", "+faststart", str(out)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return out


def make_thumb(video: Path, out: Path, t: float = 2.0) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-ss", str(t), "-i", str(video),
            "-frames:v", "1", "-vf", "scale=1280:720", str(out),
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return out


def probe_duration(path: Path) -> float:
    r = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    return float(r.stdout.strip())


def contact_sheet(images: list[Path], out: Path, cols: int = 3) -> Path:
    """Simple contact sheet via ffmpeg tile filter."""
    if not images:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    # Normalize to same size then tile
    n = len(images)
    rows = (n + cols - 1) // cols
    # Pad list to rows*cols with last image
    imgs = list(images) + [images[-1]] * (rows * cols - n)
    inputs = []
    for im in imgs:
        inputs.extend(["-i", str(im)])
    filters = "".join(f"[{i}:v]scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2,setsar=1[v{i}];" for i in range(len(imgs)))
    layout_in = "".join(f"[v{i}]" for i in range(len(imgs)))
    filt = filters + f"{layout_in}xstack=inputs={len(imgs)}:layout=" + _xstack_layout(cols, rows)
    subprocess.check_call(
        ["ffmpeg", "-y", *inputs, "-filter_complex", filt, "-frames:v", "1", str(out)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return out


def _xstack_layout(cols: int, rows: int) -> str:
    parts = []
    for r in range(rows):
        for c in range(cols):
            parts.append(f"{c*640}_{r*360}")
    return "|".join(parts)
