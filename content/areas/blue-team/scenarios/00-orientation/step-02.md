## Confirm the evidence sources are up

An investigation that starts against a half-running stack wastes an hour before
anyone notices. Check first.

```bash
curl -s http://127.0.0.1:8000/lab/status | python -m json.tool
```

Every entry under `tools` should report `"ok": true`. Then the sink:

```bash
curl -s http://127.0.0.1:8025/api/v2/messages | python -m json.tool | head -20
```

A non-zero message count is normal. This sink accumulates across every run
anyone has ever done on this machine, and nothing tags a message with the run
that produced it. That is your first real fact about this environment, and step 3
of the next scenario is where it bites.
