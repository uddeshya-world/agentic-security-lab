"""The completion badge must be earned on this instance and signed with its own key.

Two defects this guards against, both found in review (2026-10-03):

1. The signing key fell back to a constant shared by every install, so anyone
   with the repo could mint a badge that any instance verified as valid.
2. The transcript was built from a list the browser sent, so one POST with the
   right list produced a signed badge with no Run or Check behind it.

No Docker needed: content lookups are stubbed, and the ledger and key are
pointed at a temp directory.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import importlib
import json

import pytest

REQUIRED = [
    {"scenario": "00-orientation", "scenario_title": "O", "step": "step-02", "step_title": "s", "kind": "recall", "mode": "any"},
    {"scenario": "01-tool-abuse-sqli", "scenario_title": "S", "step": "step-04", "step_title": "s", "kind": "evidence", "mode": "secure"},
]
AREA = {"id": "ai-security", "title": "AI & Agent Security", "status": "available",
        "credential": {"id": "ai-security-practitioner", "title": "AI Security Practitioner", "requires_track": "core"},
        "certs": ["OWASP Top 10 for LLM Applications (2026)"]}


@pytest.fixture()
def cred(tmp_path, monkeypatch):
    monkeypatch.delenv("CREDENTIAL_SIGNING_KEY", raising=False)
    monkeypatch.setenv("CREDENTIAL_KEY_PATH", str(tmp_path / ".credential_key"))
    monkeypatch.setenv("LAB_LEDGER_PATH", str(tmp_path / "ledger.json"))
    from lab import content, credential, ledger
    importlib.reload(ledger)
    importlib.reload(credential)
    monkeypatch.setattr(content, "get_area", lambda area_id: AREA if area_id == "ai-security" else None)
    monkeypatch.setattr(credential, "required_checks", lambda area_id: [dict(r) for r in REQUIRED])
    return credential, ledger


def _forge(payload: dict, key: bytes) -> str:
    canon = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    sig = hmac.new(key, canon, hashlib.sha256).hexdigest()
    blob = json.dumps({"assertion": payload, "signature": sig}, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(blob).decode().rstrip("=")


def test_key_is_random_per_install_not_the_old_constant(cred, tmp_path):
    credential, _ = cred
    assert credential._KEY != b"cyberrange-local-issuer"
    assert len(credential._KEY) >= 64
    assert (tmp_path / ".credential_key").read_text().strip().encode() == credential._KEY


def test_badge_signed_with_the_old_shared_key_does_not_verify(cred):
    credential, _ = cred
    token = _forge({"type": "Assertion", "recipient": {"identity": "forger"}}, b"cyberrange-local-issuer")
    assert credential.verify_token(token)["valid"] is False


def test_browser_claim_alone_cannot_mint_a_badge(cred):
    credential, _ = cred
    claim = [{"scenario": r["scenario"], "step": r["step"], "kind": r["kind"], "mode": r["mode"]} for r in REQUIRED]
    out = credential.issue("ai-security", "someone", claim)
    assert out["ok"] is False
    assert "no record" in out["error"]


def test_badge_issues_from_server_ledger_and_verifies(cred):
    credential, ledger = cred
    for r in REQUIRED:
        ledger.record_pass("ai-security", r["scenario"], r["step"], r["kind"], r["mode"])
    out = credential.issue("ai-security", "learner@example.test", [])
    assert out["ok"] is True
    steps = {(t["scenario"], t["step"]) for t in out["assertion"]["evidence"]["transcript"]}
    assert steps == {(r["scenario"], r["step"]) for r in REQUIRED}
    assert credential.verify_token(out["token"])["valid"] is True


def test_partial_ledger_is_not_enough(cred):
    credential, ledger = cred
    r = REQUIRED[0]
    ledger.record_pass("ai-security", r["scenario"], r["step"], r["kind"], r["mode"])
    out = credential.issue("ai-security", "learner", [])
    assert out["ok"] is False
    assert out["eligibility"]["passed_count"] == 1
