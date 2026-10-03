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
one on their own instance. Each install has its own random key, so a badge from
one instance does not verify on another, and the transcript is built from the
server's own ledger of passed checks, not from the browser. The badge says so,
in ``verification.note``, and the verify page repeats it. Third-party attestation requires an issuer the verifier
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
import secrets
from pathlib import Path
from typing import Any

# Per-instance signing key.
#
# This used to fall back to the constant "cyberrange-local-issuer", which made
# every install share one key: anyone with the repo could mint a badge that any
# other instance would call valid. Now: a hosted issuer supplies
# CREDENTIAL_SIGNING_KEY; otherwise each install generates 32 random bytes on
# first use and keeps them next to the lab data (gitignored). If that file can't
# be written, the key lives only for this process -- badges then stop verifying
# after a restart, which is the safe way to fail.
_LEGACY_KEY = b"cyberrange-local-issuer"


def _key_path() -> Path:
    env = os.environ.get("CREDENTIAL_KEY_PATH")
    if env:
        return Path(env)
    if Path("/data").is_dir() and os.access("/data", os.W_OK):
        return Path("/data/.credential_key")
    return Path(__file__).resolve().parents[1] / "data" / ".credential_key"


def _load_key() -> bytes:
    env = os.environ.get("CREDENTIAL_SIGNING_KEY")
    if env:
        return env.encode("utf-8")
    path = _key_path()
    try:
        existing = path.read_text(encoding="utf-8").strip()
        if len(existing) >= 32:
            return existing.encode("utf-8")
    except OSError:
        pass
    fresh = secrets.token_hex(32)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(fresh, encoding="utf-8")
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    except OSError as e:
        print(f"[credential] signing key not persisted ({e}); badges will not survive a restart", flush=True)
    return fresh.encode("utf-8")


_KEY = _load_key()

BADGE_CONTEXT = "https://w3id.org/openbadges/v2"
ISSUER_NAME = "CyberRange (self-hosted instance)"


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sign(payload: dict[str, Any]) -> str:
    return hmac.new(_KEY, _canonical(payload), hashlib.sha256).hexdigest()


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def required_checks(area_id: str) -> list[dict[str, Any]]:
    """Graded steps the Area actually requires for the badge.

    If ``credential.requires_track`` is set (AI Security: ``core``), only that
    track counts. Advanced labs stay optional.
    """
    from lab import content

    area = content.get_area(area_id) or {}
    req_track = (area.get("credential") or {}).get("requires_track")
    out: list[dict[str, Any]] = []
    for scen in content.list_scenarios(area_id):
        if req_track and (scen.get("track") or "core") != req_track:
            continue
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
    """Compare a list of passes against what the Area actually requires.

    ``issue`` calls this with the server-side ledger (``lab.ledger``), which only
    holds checks this instance graded as passed. A browser-supplied list is only
    ever compared to explain a mismatch, never signed.
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

    # An Area still being authored has an incomplete scenario set, so "all graded checks
    # passed" means something different today than it will next month. Signing that as a
    # credential would make two badges with the same name assert different work. Only an
    # Area whose content is frozen (`status: available`) can mint.
    if (area.get("status") or "available") != "available":
        return {
            "ok": False,
            "error": (
                f"{area.get('title') or area_id} is still being authored, so its "
                "credential is not issuable yet. Progress is kept; the badge unlocks "
                "when the Area is published."
            ),
            "area_status": area.get("status"),
        }

    # Grade against what this server saw pass, never against the browser's list.
    # The browser's list is kept only to explain a mismatch to the learner.
    from lab import ledger

    recorded = ledger.passes(area_id)
    elig = eligibility(area_id, recorded)
    if not elig["eligible"]:
        claimed = eligibility(area_id, passed)
        msg = "Not every graded check has been passed yet."
        if claimed["eligible"]:
            msg = (
                "This browser says every check passed, but this lab instance has no record "
                "of some of them. Run and Check those steps here, then claim again."
            )
        return {"ok": False, "error": msg, "eligibility": elig}
    passed = recorded

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
                    f"Passed all {elig['required_count']} graded checks on the "
                    f"{(cred.get('requires') or 'required')} path in {area.get('title')}. "
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
