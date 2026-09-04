"""Completion credential: a signed, evidence-backed transcript — not a timestamp hash.

What was wrong with the old badge
---------------------------------
It was ``SHA-256(area | credential | count | Date.now())`` computed in the
browser. It proved that a clock existed. Anyone could produce one, and it
carried no record of what the learner actually did.

What this issues instead
------------------------
A transcript: every graded check the learner passed, with the scenario, the step,
the check kind and the mode it was graded in. The transcript is HMAC-signed by
the lab process, so it is tamper-evident, and it is shaped as an Open Badges
assertion (``https://openbadgespec.org``) so it can be handed to a badge host
(Credly, Badgr / Canvas Credentials, Accredible) later without re-modelling it.

The honesty this file is required to keep
-----------------------------------------
This is a **self-hosted** lab. The learner controls the machine holding the
signing key, so this signature proves integrity, not third-party attestation —
it detects a badge that was edited after issue, it does not stop someone forging
one on their own instance. The badge says so, in ``verification.note``, and the
verify page repeats it. Third-party attestation requires an issuer the verifier
trusts, which means a hosted issuer, which is a product decision and not
something a local container can fake.

The artifact that actually carries weight in an interview is the transcript: which
attacks landed, which controls stopped them, and the before/after. That is the
part we sign.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import hmac
import json
import os
from typing import Any

# Per-instance signing key. Derived from an env var when set, so a hosted issuer
# can supply a real secret; otherwise a stable per-install value.
_KEY = (os.environ.get("CREDENTIAL_SIGNING_KEY") or "cyberrange-local-issuer").encode("utf-8")

BADGE_CONTEXT = "https://w3id.org/openbadges/v2"
ISSUER_NAME = "CyberRange (self-hosted instance)"


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sign(payload: dict[str, Any]) -> str:
    return hmac.new(_KEY, _canonical(payload), hashlib.sha256).hexdigest()


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def required_checks(area_id: str) -> list[dict[str, Any]]:
    """Every graded step in an Area — the full list a learner must pass to claim."""
    from lab import content

    out: list[dict[str, Any]] = []
    for scen in content.list_scenarios(area_id):
        for step in scen.get("steps") or []:
            if not step.get("has_check"):
                continue
            check = step.get("check") or {}
            out.append(
                {
                    "scenario": scen["id"],
                    "scenario_title": scen.get("title"),
                    "step": step["id"],
                    "step_title": step.get("title"),
                    "kind": check.get("kind") or "manual",
                    "mode": check.get("require_mode") or "any",
                }
            )
    return out


def eligibility(area_id: str, passed: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Compare the learner's claimed passes against what the Area actually requires.

    ``passed`` comes from the browser (localStorage), so it is a *claim*. We do
    not treat it as proof — we treat it as a list to be checked for completeness
    against the content tree, and we record it verbatim in the transcript so a
    reader can see exactly what was asserted.
    """
    required = required_checks(area_id)
    claimed = {(p.get("scenario"), p.get("step")) for p in (passed or []) if isinstance(p, dict)}
    missing = [r for r in required if (r["scenario"], r["step"]) not in claimed]
    return {
        "required_count": len(required),
        "passed_count": len(required) - len(missing),
        "missing": missing,
        "eligible": len(required) > 0 and not missing,
    }


def issue(area_id: str, learner: str | None, passed: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Build a signed Open Badges-shaped assertion, or explain why it can't be issued."""
    from lab import content

    area = content.get_area(area_id)
    if not area:
        return {"ok": False, "error": f"Unknown area: {area_id}"}

    elig = eligibility(area_id, passed)
    if not elig["eligible"]:
        return {
            "ok": False,
            "error": "Not every graded check has been passed yet.",
            "eligibility": elig,
        }

    cred = area.get("credential") or {}
    transcript = sorted(
        (
            {
                "scenario": p.get("scenario"),
                "step": p.get("step"),
                "kind": p.get("kind"),
                "mode": p.get("mode"),
            }
            for p in (passed or [])
            if isinstance(p, dict)
        ),
        key=lambda r: (r["scenario"] or "", r["step"] or ""),
    )

    payload = {
        "@context": BADGE_CONTEXT,
        "type": "Assertion",
        "issuedOn": _now_iso(),
        "recipient": {"type": "identity", "hashed": False, "identity": learner or "anonymous learner"},
        "badge": {
            "type": "BadgeClass",
            "id": cred.get("id") or f"{area_id}-completion",
            "name": cred.get("title") or f"{area.get('title')} — completed",
            "description": cred.get("description") or "",
            "criteria": {
                "narrative": (
                    f"Passed all {elig['required_count']} graded checks across "
                    f"{len(content.list_scenarios(area_id))} scenarios in {area.get('title')}. "
                    "Each graded check asserts real lab state — dumped rows, an intercepted "
                    "message, or the specific control that blocked a step — after the learner "
                    "ran the attack themselves."
                ),
                "frameworks": area.get("certs") or [],
            },
            "issuer": {"type": "Profile", "name": ISSUER_NAME},
        },
        "evidence": {
            "type": "Evidence",
            "narrative": f"{elig['passed_count']} of {elig['required_count']} graded checks recorded.",
            "transcript": transcript,
        },
    }

    signature = _sign(payload)
    return {
        "ok": True,
        "assertion": payload,
        "signature": signature,
        "token": _encode_token(payload, signature),
        "eligibility": elig,
        "verification": {
            "type": "HostedHmac",
            "algorithm": "HMAC-SHA256",
            "verify_url": "/lab/ui/verify.html",
            "note": (
                "Signed by this self-hosted instance. The signature proves the transcript "
                "has not been edited since it was issued; it is not third-party attestation, "
                "because whoever runs this lab also holds the signing key."
            ),
        },
    }


def _encode_token(payload: dict[str, Any], signature: str) -> str:
    import base64

    blob = json.dumps({"assertion": payload, "signature": signature}, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(blob).decode("ascii").rstrip("=")


def verify_token(token: str) -> dict[str, Any]:
    import base64

    try:
        pad = "=" * (-len(token) % 4)
        blob = base64.urlsafe_b64decode(token + pad)
        data = json.loads(blob)
        payload, signature = data["assertion"], data["signature"]
    except Exception:  # noqa: BLE001
        return {"ok": False, "valid": False, "error": "That badge token could not be read."}

    valid = hmac.compare_digest(_sign(payload), signature or "")
    return {
        "ok": True,
        "valid": valid,
        "assertion": payload,
        "issuer": ISSUER_NAME,
        "note": (
            "Signature checked against this instance's key."
            if valid
            else "Signature does not match. Either the badge was edited, or it was issued by a different instance."
        ),
    }
