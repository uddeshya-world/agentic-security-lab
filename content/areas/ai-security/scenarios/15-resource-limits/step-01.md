## Why the step cap isn't enough

`agents/executor.py` already has:

```python
MAX_PLAN_STEPS = int(os.environ.get("MAX_PLAN_STEPS", "8"))
```

That bounds one plan. It does **not** bound:

| Gap | What slips through |
|---|---|
| **Cost** | 8 steps that each retrieve huge context still burns real spend |
| **Repetition** | the same call re-issued in a loop across many short plans |
| **Rate** | one session issuing calls far faster than any human workflow |
| **Aggregate** | many "valid" plans in sequence adding up to an outage or a bill |

The mental shift: stop asking *"is this call allowed?"* and start asking
*"is this **volume and shape** of calls plausible for a real user?"* A counter
answers the first question. Budgets, loop detection, and rate limits answer the
second.
