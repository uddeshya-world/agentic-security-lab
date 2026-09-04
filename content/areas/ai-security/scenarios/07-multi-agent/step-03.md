## Sign messages, allow-list agents

Open `defenses/m03/signing.py`. Secure mode adds two controls:

```python
sig = sign(plan)              # planner HMACs the canonical message
...
if not verify(tampered, sig): reject   # executor detects any change
if tool not in ALLOWED_TOOLS: reject   # registry allow-list
```

- **C9 — authenticated inter-agent messages.** The planner signs; the executor
  verifies before acting. Rewriting any field breaks the signature, so tampering
  is detected, not executed.
- **C10 — agent/tool registry allow-list.** Only registered agents and tools are
  permitted; a rogue `shell_tool` is refused before invocation.

In production the shared HMAC key becomes per-agent identities (mTLS, signed
envelopes), but the property is identical: **a message you can't authenticate is
an instruction you can't trust.**
