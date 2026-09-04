## Two gates on the send tool

Secure mode adds two independent controls to `email_tool`:

**Egress allow-list (C4)** — only recipients on domains you own are permitted:

```python
# tools/email_tool/server.py (secure branch)
if is_secure() and not to.endswith("@example.test"):
    return {"error": "recipient domain not on allow-list"}
```

**Human-in-the-loop (C5)** — side-effect tools default to *deny* unless a human
approves (simulated in the lab by `LAB_APPROVE`):

```python
# defenses/m01/approval_gate.py
if requires_approval(tool) and not approved():
    raise ApprovalDenied(tool)
```

Either one alone breaks the chain. Together they are defense in depth: even if a
recipient somehow passed the allow-list, the human gate still stops an
unattended bulk export.

Enable secure mode (console toggle, or recreate the stack) for the graded run.
