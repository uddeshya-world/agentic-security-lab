"""Shared FastAPI scaffolding for the lab's MCP-style tool servers.

Each tool server exposes the same three-route contract: GET /schema (tool's
parameter schema), POST /invoke (execute with given args), GET /health
(liveness). This mimics MCP's discover-then-call shape without depending on
the real MCP transport/SDK -- see plan section 3 for why.

SECURE_MODE is normally read from this process's own env. The guided lesson
engine can also force the mode for a single request by sending an
``X-Secure-Mode`` header (set by the agent's tool registry while a graded check
runs). ``is_secure()`` honors that per-request override first, then falls back
to the env var, so the persistent container mode and health badge are unchanged
outside a check.
"""
import contextvars
import os
from typing import Any, Callable

from fastapi import FastAPI, Request
from pydantic import BaseModel

_req_override: contextvars.ContextVar[bool | None] = contextvars.ContextVar(
    "tool_secure_override", default=None
)


def _env_secure() -> bool:
    return os.environ.get("SECURE_MODE", "false").lower() in ("1", "true", "yes")


def is_secure() -> bool:
    ov = _req_override.get()
    if ov is not None:
        return ov
    return _env_secure()


def _header_override(request: Request) -> bool | None:
    raw = request.headers.get("x-secure-mode")
    if raw is None:
        return None
    return raw.strip().lower() in ("1", "true", "yes")


class InvokeResult(BaseModel):
    result: Any
    side_effects: list[dict] = []


def make_tool_app(
    name: str,
    schema_provider: Callable[[], dict],
    invoke_handler: Callable[[dict], InvokeResult],
) -> FastAPI:
    app = FastAPI(title=f"{name} tool server")

    @app.get("/health")
    def health(request: Request):
        ov = _header_override(request)
        secure = ov if ov is not None else _env_secure()
        return {"status": "ok", "tool": name, "secure_mode": secure}

    @app.get("/schema")
    def schema():
        return schema_provider()

    @app.post("/invoke")
    def invoke(args: dict, request: Request):
        token = _req_override.set(_header_override(request))
        try:
            return invoke_handler(args)
        finally:
            _req_override.reset(token)

    return app
