#!/usr/bin/env python3
"""Kokoro-82M TTS helper for Core explainer videos.

Voice: bf_emma (British English female). Loudness normalized to ~-16 LUFS.
Uses the prebuilt venv at /workspace/video-build/.venv by default.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_VENV_PYTHON = Path("/workspace/video-build/.venv/bin/python")
VOICE = "bf_emma"
LANG = "b"
TARGET_LUFS = -16.0
SAMPLE_RATE = 24000

_pipeline = None


def _ensure_kokoro_import():
    """Prefer the video-build venv if we are not already inside it."""
    try:
        import kokoro  # noqa: F401
        return
    except ImportError:
        pass
    py = os.environ.get("VIDEO_VENV_PYTHON", str(DEFAULT_VENV_PYTHON))
    if Path(py).exists() and Path(py).resolve() != Path(sys.executable).resolve():
        os.execv(py, [py, *sys.argv])
    raise SystemExit("kokoro not installed; use /workspace/video-build/.venv")


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        from kokoro import KPipeline
        _pipeline = KPipeline(lang_code=LANG, repo_id="hexgrad/Kokoro-82M")
    return _pipeline


def synthesize(text: str, out_wav: Path, speed: float = 1.0) -> float:
    """Synthesize text to WAV (PCM16 mono 24kHz). Returns duration seconds."""
    import numpy as np
    import soundfile as sf

    out_wav = Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    pipe = get_pipeline()
    chunks = []
    for _, _, audio in pipe(text, voice=VOICE, speed=speed):
        chunks.append(audio.numpy() if hasattr(audio, "numpy") else audio)
    if not chunks:
        raise RuntimeError(f"TTS produced no audio for: {text[:80]!r}")
    audio = np.concatenate(chunks)
    raw = out_wav.with_suffix(".raw.wav")
    sf.write(str(raw), audio, SAMPLE_RATE, subtype="PCM_16")
    loudnorm(raw, out_wav)
    raw.unlink(missing_ok=True)
    return wav_duration(out_wav)


def loudnorm(src: Path, dst: Path, target_lufs: float = TARGET_LUFS) -> None:
    """Two-pass ffmpeg loudnorm to target integrated loudness."""
    # Measure
    probe = subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-i", str(src),
            "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11:print_format=json",
            "-f", "null", "-",
        ],
        capture_output=True, text=True,
    )
    # loudnorm prints JSON on stderr
    err = probe.stderr
    start = err.rfind("{")
    end = err.rfind("}")
    if start < 0 or end < 0:
        # Fallback: copy
        subprocess.check_call(["ffmpeg", "-y", "-i", str(src), str(dst)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    meta = json.loads(err[start : end + 1])
    filt = (
        f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11:"
        f"measured_I={meta['input_i']}:"
        f"measured_TP={meta['input_tp']}:"
        f"measured_LRA={meta['input_lra']}:"
        f"measured_thresh={meta['input_thresh']}:"
        f"offset={meta['target_offset']}:"
        f"linear=true:print_format=summary"
    )
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(src), "-af", filt, str(dst)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def wav_duration(path: Path) -> float:
    with wave.open(str(path)) as w:
        return w.getnframes() / float(w.getframerate())


def concat_wavs(paths: list[Path], out: Path, gap_s: float = 0.15) -> float:
    """Concatenate WAVs with a short silence gap. All must be same format."""
    import numpy as np
    import soundfile as sf

    parts = []
    gap = np.zeros(int(SAMPLE_RATE * gap_s), dtype=np.float32)
    for i, p in enumerate(paths):
        data, sr = sf.read(str(p), dtype="float32")
        if sr != SAMPLE_RATE:
            raise RuntimeError(f"sample rate mismatch: {p}")
        parts.append(data)
        if i < len(paths) - 1:
            parts.append(gap)
    audio = np.concatenate(parts) if parts else np.zeros(1, dtype=np.float32)
    out.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(out), audio, SAMPLE_RATE, subtype="PCM_16")
    return float(len(audio)) / SAMPLE_RATE


if __name__ == "__main__":
    _ensure_kokoro_import()
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("text")
    ap.add_argument("-o", "--out", default="sample.wav")
    ap.add_argument("--speed", type=float, default=1.0)
    a = ap.parse_args()
    dur = synthesize(a.text, Path(a.out), speed=a.speed)
    print(f"voice={VOICE} duration={dur:.2f}s out={a.out}")
