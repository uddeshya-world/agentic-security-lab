"""In-memory ring buffer of lab simulation events for the Lab Console UI."""
from __future__ import annotations

import itertools
import threading
from collections import deque
from datetime import datetime, timezone
from typing import Any

_lock = threading.Lock()
_seq = itertools.count(1)
_events: deque[dict[str, Any]] = deque(maxlen=500)


def clear_events() -> None:
    with _lock:
        _events.clear()


def emit(
    phase: str,
    message: str,
    *,
    actor: str = "lab",
    detail: dict[str, Any] | None = None,
    secure_mode: bool | None = None,
    outcome: str = "info",
) -> dict[str, Any]:
    event = {
        "id": next(_seq),
        "ts": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "actor": actor,
        "message": message,
        "detail": detail or {},
        "secure_mode": secure_mode,
        "outcome": outcome,
    }
    with _lock:
        _events.append(event)
    print(
        f"[lab-event] {event['id']} {phase}/{actor} {outcome}: {message}",
        flush=True,
    )
    return event


def list_events(since_id: int = 0, limit: int = 200) -> list[dict[str, Any]]:
    with _lock:
        items = [e for e in _events if e["id"] > since_id]
    return items[-limit:]
