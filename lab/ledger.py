"""Server-side record of graded checks this instance has actually seen pass.

Why this exists
---------------
The completion badge used to be built from a list the *browser* sent
(``localStorage``). The server checked that the list was complete, then signed
it. So one POST with the right list produced a valid badge without a single Run
or Check, and the signature made that look like evidence.

The badge is now built from this ledger instead. A pass lands here only when
``POST /scenario/{area}/{scenario}/check/{step}`` returns ``passed: true`` on
this process, so the transcript is a record of checks the server graded, not a
claim it was handed.

Single-user and local, like the rest of the lab. Persisted as JSON next to the
other lab data so a container restart does not wipe a learner's progress.
"""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any

_lock = threading.Lock()


def _default_path() -> Path:
    env = os.environ.get("LAB_LEDGER_PATH")
    if env:
        return Path(env)
    # Inside compose the agent mounts ./data at /data; on the host, use the repo's data/.
    if Path("/data").is_dir() and os.access("/data", os.W_OK):
        return Path("/data/ledger.json")
    return Path(__file__).resolve().parents[1] / "data" / "ledger.json"


PATH = _default_path()


def _load() -> dict[str, Any]:
    try:
        return json.loads(PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"passes": {}}


def _save(data: dict[str, Any]) -> None:
    try:
        PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=1, sort_keys=True), encoding="utf-8")
        tmp.replace(PATH)
    except OSError as e:  # read-only volume: keep working in memory for this process
        print(f"[ledger] could not persist progress: {e}", flush=True)


_data = _load()


def record_pass(area_id: str, scenario_id: str, step_id: str, kind: str | None, mode: str | None) -> None:
    """Called by the check route, and only when the check passed."""
    key = f"{area_id}/{scenario_id}/{step_id}"
    with _lock:
        _data.setdefault("passes", {})[key] = {
            "area": area_id,
            "scenario": scenario_id,
            "step": step_id,
            "kind": kind or "manual",
            "mode": mode or "any",
            "at": int(time.time()),
        }
        _save(_data)


def passes(area_id: str) -> list[dict[str, Any]]:
    """Every pass recorded for an Area, in the shape ``credential`` expects."""
    with _lock:
        rows = [dict(v) for v in (_data.get("passes") or {}).values() if v.get("area") == area_id]
    return sorted(rows, key=lambda r: (r["scenario"], r["step"]))


def clear(area_id: str | None = None) -> None:
    with _lock:
        if area_id is None:
            _data["passes"] = {}
        else:
            _data["passes"] = {k: v for k, v in (_data.get("passes") or {}).items() if v.get("area") != area_id}
        _save(_data)
