## Attest before trust

Open `defenses/m07/attestation.py`. Secure mode runs `attest()` on every
component before it can be used:

```python
if manifest is None:                      reject  # no manifest → unverified
if tool not in TRUSTED_MANIFESTS:         reject  # not pinned/allow-listed
if not valid_signature(manifest):         reject  # tampered or unsigned
if asked_caps - declared_caps:            reject  # capability escalation
```

This is **control C15 — supply-chain attestation**. Each legitimate tool ships a
**signed capability manifest** (name, publisher, capabilities). At startup /
before invoke, anything missing, unsigned, unknown, or over-scoped is refused —
fail closed.

- The rogue `backdoor_tool` has no manifest → refused.
- The tampered `file_tool` requested `exec` beyond its signed manifest → refused,
  and its signature no longer matches.

In production this is your SBOM, pinned versions, and image/plugin signing — the
same provenance discipline, applied to the agent's tools.
