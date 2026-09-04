"""Shared helpers for Module 1 Layer-A (tool-direct) attack scripts."""
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

DB_TOOL_URL = os.environ.get("DB_TOOL_URL_HOST", "http://127.0.0.1:8101")
EMAIL_TOOL_URL = os.environ.get("EMAIL_TOOL_URL_HOST", "http://127.0.0.1:8102")
FILE_TOOL_URL = os.environ.get("FILE_TOOL_URL_HOST", "http://127.0.0.1:8103")
AGENT_URL = os.environ.get("AGENT_URL", "http://127.0.0.1:8000")
MAILHOG_API = os.environ.get("MAILHOG_API_BASE", "http://127.0.0.1:8025")

RESULTS_DIR = Path(__file__).resolve().parents[2] / "metrics" / "m01" / "results"


@dataclass
class AttackResult:
    attack_id: str
    name: str
    layer: str  # "A" tool-direct
    secure_mode: bool
    success: bool  # True = attack worked (exploit succeeded)
    blocked: bool  # True = defense stopped the attack
    detail: str
    evidence: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def tool_secure_mode(url: str) -> bool:
    try:
        r = httpx.get(f"{url}/health", timeout=5.0)
        r.raise_for_status()
        return bool(r.json().get("secure_mode", False))
    except Exception:
        return os.environ.get("SECURE_MODE", "false").lower() in ("1", "true", "yes")


def invoke_tool(base_url: str, args: dict, timeout: float = 30.0) -> dict:
    r = httpx.post(f"{base_url}/invoke", json=args, timeout=timeout)
    r.raise_for_status()
    return r.json()


def write_result(result: AttackResult) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    mode = "secure" if result.secure_mode else "vuln"
    path = RESULTS_DIR / f"{result.attack_id}_{mode}.json"
    path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    return path


def print_result(result: AttackResult) -> None:
    status = "SUCCESS (exploit landed)" if result.success else (
        "BLOCKED" if result.blocked else "FAILED"
    )
    print(f"[{result.attack_id}] {result.name} | SECURE_MODE={result.secure_mode} | {status}")
    print(f"  {result.detail}")
    path = write_result(result)
    print(f"  wrote {path}")


def exit_for_result(result: AttackResult) -> None:
    """Exit 0 always for metrics aggregation; attack scripts report via JSON."""
    print_result(result)
    # Non-zero only on infrastructure errors (caller raises before this).
    sys.exit(0)
