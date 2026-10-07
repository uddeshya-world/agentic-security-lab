# Core path explainer videos

Nine short explainers for the CyberRange Core track. Scripts in
[`CORE_VIDEO_SCRIPTS.md`](CORE_VIDEO_SCRIPTS.md) are the source of truth for beats
and narration; lab UI strings win when they differ.

## Where the published videos live

The rendered MP4s are **not** in git, so a student's clone stays small. They are
assets of the GitHub release
[`videos-v1`](https://github.com/uddeshya-world/agentic-security-lab/releases/tag/videos-v1),
and the Pages workflow copies them to
`https://uddeshya-world.github.io/agentic-security-lab/video/NN-<id>.mp4`, where the
lessons and the README play them. Captions (WebVTT) and posters for the lessons are in
`lab/ui/video/`.

To publish a rebuild, create a new release (`videos-v2`, ...) with the new files, then
point `VIDEO_RELEASE` in `.github/workflows/pages.yml` at it.

## Outputs

Rendered files land in `out/` (gitignored):

| File | Spec |
|------|------|
| `NN-<id>.mp4` | 1920×1080, 30 fps, H.264 + AAC, burned-in captions |
| `NN-<id>.srt` | Sidecar captions |
| `NN-<id>-thumb.png` | 1280×720 poster |

Videos (order):

1. `00-orientation`
2. `01-tool-abuse-sqli`
3. `16-direct-injection`
4. `02-rag-poisoning`
5. `03-cross-tool-exfil`
6. `17-data-guards`
7. `18-agent-identity`
8. `04-agent-exploit`
9. `05-guardrail-map`

## Voice

- Engine: **Kokoro-82M** (Apache-2.0), local CPU, no cloud TTS
- Voice: **`bf_emma`** (British English female) — scripts use British wording (boot, glovebox, judgement)
- Loudness: normalized to about **−16 LUFS** via ffmpeg `loudnorm`
- Venv used by the build: `/workspace/video-build/.venv` (override with `VIDEO_VENV`)

## Design tokens

Slides and overlays use the lab dark theme tokens from `lab/ui/cyberrange.css`
(copied to `assets/cyberrange.css` for offline slide HTML):

- Ground: `--void` `#0a0c10`, `--plate` `#12161c`, …
- Accents: `--ember` `#ff6b35`, `--halon` `#35e0c0`, `--brass` `#e8b84b`
- Type: Space Grotesk / Archivo / JetBrains Mono

Lab footage is captured with Playwright against `http://127.0.0.1:8000` with
`data-theme=dark` forced (headless Chromium otherwise prefers light).

## Layout

```
docs/video/
  CORE_VIDEO_SCRIPTS.md   # source of truth
  README.md
  build.sh / build.py     # one-command rebuild
  tts.py / slides.py / capture.py / compose.py
  assets/                 # CSS + brand marks for slides
  src/
    scripts.json          # structured beats
    narration/<id>/       # plain-text lines
    audio/<id>/           # per-beat WAV (bf_emma, loudnorm)
    slides/<id>/          # HTML + PNG synthetic frames
    captures/<id>/        # Playwright lab PNGs
    captions/<id>.ass     # burn-in captions (1080p-native ASS, generated)
    beats/<id>.json       # resolved plan + timings
    NARRATION_DELTAS.md   # script vs lab-UI differences
  out/                    # mp4 / srt / thumb / contact sheet (gitignored)
```

## Rebuild

Lab must be up on this compose project (`agentic-security-lab-video`):

```bash
cd /workspace/agentic-security-lab-video
sudo docker compose up -d
# if tool calls time out, re-ACCEPT DOCKER-USER for the current bridge

# Full rebuild (TTS + slides + lab capture + ffmpeg)
./docs/video/build.sh

# One video
./docs/video/build.sh --only 00-orientation

# Re-compose only (reuse audio/slides/captures)
./docs/video/build.sh --skip-tts --skip-slides --skip-capture
```

Dependencies: `ffmpeg` / `ffprobe`, Playwright Chromium, Kokoro in the video-build
venv (`pillow`, `numpy`, `soundfile`, `kokoro`, `playwright`).

## How a video is built

1. `scripts.json` holds the beats parsed from `CORE_VIDEO_SCRIPTS.md`. `build.py` renders
   `src/narration/<id>/*.txt`.
2. `tts.py` speaks each beat with Kokoro `bf_emma` and normalizes it with two-pass `loudnorm`
   (I=−16, TP=−1.5).
3. `slides.py` renders the analogy, diagram, "Where the analogy breaks" and end-card frames as
   HTML with the cyberrange tokens, then screenshots them at 1920×1080.
4. `capture.py` drives the real lab with Playwright at 2× scale (3840×2160) in dark theme. It
   dismisses the Area scope gate, opens each run step, sets vulnerable or secure, presses
   **Run the attack**, and waits for the timeline. MailHog is emptied before the exfil run so
   the shot shows exactly one message.
5. `compose.py` holds each frame for the script's beat length (never shorter than the speech).
   Lab shots get an eased push-in toward the timeline. Clips are joined, an SRT sidecar is
   written, ASS captions are burned in, and the thumbnail and contact sheet are rendered.

Timing: each beat's screen time comes from the script timestamps, scaled to the script's
`target_duration_s`. Every video lands within ±1 s of its target (75–90 s).

## Rules

- Synthetic data only — no real PII, faces, or third-party logos
- Never say “certified” / “certification” (say completion badge)
- Keep “Where the analogy breaks” beats
- Do not upload or link videos from lessons until published
