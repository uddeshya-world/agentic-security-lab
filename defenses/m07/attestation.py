"""Module 7 defense: supply-chain attestation for tools / MCP servers.

An agent's tools are its supply chain. A malicious or tampered tool server —
added without review, or behaving until triggered — runs with the agent's
privileges. The controls here are a registry of **signed capability manifests**:
each legitimate tool ships a manifest (name, capabilities, publisher) plus a
signature over it. At startup / before invoke, ``attest`` refuses any tool whose
manifest is missing, unsigned, tampered, or whose capabilities exceed what the
manifest declares.
"""
from __future__ import annotations

import hashlib
import hmac
import json

_SUPPLY_KEY = b"agentic-security-lab-m07-supply-key"

# The trusted manifest set (what a reviewed, pinned SBOM would encode).
TRUSTED_MANIFESTS = {
    "db_tool": {"publisher": "lab-core", "capabilities": ["read"]},
    "email_tool": {"publisher": "lab-core", "capabilities": ["send"]},
    "file_tool": {"publisher": "lab-core", "capabilities": ["read", "write"]},
}


def _sig(manifest: dict) -> str:
    body = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(_SUPPLY_KEY, body, hashlib.sha256).hexdigest()


def sign_manifest(manifest: dict) -> dict:
    """Produce a signed manifest for a legitimately published tool."""
    return {**manifest, "signature": _sig({k: v for k, v in manifest.items() if k != "signature"})}


def attest(tool_name: str, manifest: dict | None) -> tuple[bool, str]:
    """Return (trusted, reason). Fail closed on anything unverified."""
    if manifest is None:
        return False, f"no capability manifest for '{tool_name}' — refusing unverified component"
    if tool_name not in TRUSTED_MANIFESTS:
        return False, f"'{tool_name}' is not in the pinned/allow-listed registry"
    provided_sig = manifest.get("signature")
    body = {k: v for k, v in manifest.items() if k != "signature"}
    if not provided_sig or not hmac.compare_digest(_sig(body), provided_sig):
        return False, f"manifest signature invalid for '{tool_name}' — tampered or unsigned"
    declared = set(TRUSTED_MANIFESTS[tool_name]["capabilities"])
    asked = set(manifest.get("capabilities", []))
    if not asked.issubset(declared):
        return False, f"'{tool_name}' requests capabilities beyond its manifest: {sorted(asked - declared)}"
    return True, f"'{tool_name}' attested (publisher={manifest.get('publisher')})"
