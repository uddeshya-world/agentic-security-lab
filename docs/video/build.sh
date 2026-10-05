#!/usr/bin/env bash
# Rebuild all Core explainer videos (or pass --only IDs).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="${VIDEO_VENV:-/workspace/video-build/.venv}"
PY="${VENV}/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "Missing TTS/playwright venv at $VENV" >&2
  exit 1
fi
export VIDEO_VENV_PYTHON="$PY"
exec "$PY" "$ROOT/build.py" "$@"
