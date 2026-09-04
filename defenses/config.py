"""Single source of truth for the SECURE_MODE toggle.

Read once; every tool wrapper and the executor's choke point call is_secure()
from here (or from tools.base.is_secure(), which reads the same env var
independently inside each tool-server process). Keeping the var name identical
(SECURE_MODE) across processes is what makes the before/after metrics diff an
honest single-toggle comparison.

The guided lesson engine needs to run the *same* attack in vulnerable and
secure mode without recreating containers (advisor invariant: graded steps are
deterministic and the app owns the toggle). It does this with a per-request
override held in a contextvar: while a check runs, ``secure_override(True/False)``
forces the mode for that call only, in this process. ``tools.registry`` reads
the same override and propagates it to tool servers via the ``X-Secure-Mode``
header, so the executor path and the tool servers agree. Outside an override the
container's ``SECURE_MODE`` env is authoritative, so the persistent stack and the
status badge are unaffected.
"""
import contextvars
import os
from contextlib import contextmanager

_override: contextvars.ContextVar[bool | None] = contextvars.ContextVar(
    "secure_override", default=None
)


def _env_secure() -> bool:
    return os.environ.get("SECURE_MODE", "false").lower() in ("1", "true", "yes")


def is_secure() -> bool:
    ov = _override.get()
    if ov is not None:
        return ov
    return _env_secure()


def get_override() -> bool | None:
    """Current per-request override, or None when the env value is authoritative."""
    return _override.get()


@contextmanager
def secure_override(value: bool | None):
    """Force secure/vulnerable mode for the duration of the block (this process).

    ``value=None`` is a no-op (env stays authoritative), which maps cleanly to a
    check's ``require_mode: "any"``.
    """
    token = _override.set(value)
    try:
        yield
    finally:
        _override.reset(token)
