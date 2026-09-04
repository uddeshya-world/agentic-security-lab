## Policy-as-code + audit

Secure mode routes every action through `policy/engine.py`:

```python
verdict = evaluate(tool, args)   # allow / deny / require_approval by blast radius
# extra rule: email to a non-owned domain is always denied
# every evaluation appends to a queryable audit trail
```

Two controls:

- **C16 — policy-as-code decision matrix.** Low-blast actions auto-allow;
  high/critical actions require human approval; external egress is denied
  outright. The disposition is derived from data, so it's consistent and
  reviewable.
- **C17 — audit trail.** Every decision records **who** (agent), **what**
  (tool + args), the **decision**, **why** (the rule), and **when** — queryable
  after the fact, unlike raw logs.

This is the "secure-by-default" posture the whole Area builds toward: a new agent
inherits the policy and the audit trail without re-deriving security from scratch.
