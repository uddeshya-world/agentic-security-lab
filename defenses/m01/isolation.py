"""Minimal isolation wrapper for tool invocation.

v1.0 does NOT claim container sandbox escape prevention. This wrapper only:
- enforces a wall-clock timeout around the invoke callable
- refuses shell-style tool names

True subprocess/seccomp isolation is a future module.
"""
from __future__ import annotations

import concurrent.futures
from typing import Any, Callable


class IsolationError(RuntimeError):
    pass


DEFAULT_TIMEOUT_S = 30.0


def run_isolated(
    fn: Callable[[], Any],
    *,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    tool_name: str = "",
) -> Any:
    if tool_name and any(c in tool_name for c in ("|", ";", "`", "$")):
        raise IsolationError(f"refusing suspicious tool name: {tool_name!r}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        fut = pool.submit(fn)
        try:
            return fut.result(timeout=timeout_s)
        except concurrent.futures.TimeoutError as e:
            raise IsolationError(f"tool invoke timed out after {timeout_s}s") from e
