## Validate on write, authenticate on read

Open `defenses/m04/memory_guard.py`. Secure mode adds two controls:

```python
# C11 — write validation: memory holds facts, not commands
if looks_like_instruction(content): reject_write

# C12 — provenance signing: HMAC-tag on write, verify on recall
stored = tag(content)                       # "sig:<hmac>:<content>"
content = verify_and_strip(stored) or DROP  # unsigned/tampered → quarantined
```

- **C11 — write validation** rejects entries that read as instructions to the
  agent, so the backdoor never enters the store.
- **C12 — provenance signing** HMAC-tags every accepted entry. An entry written
  around the guard (e.g. an attacker with direct DB access) is unsigned, so it
  fails verification and is quarantined on recall. Tampering a stored row breaks
  its signature the same way.

Together they give defense in depth: the poison is stopped at write, and even a
direct-to-database write is caught at read.
