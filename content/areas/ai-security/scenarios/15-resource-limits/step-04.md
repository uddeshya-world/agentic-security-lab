## Which control fired?

Run it in secure mode. The **Check** confirms the runaway is stopped early — and
the timeline names the control:

```
GUARDRAIL (loop-detector): identical call repeated more than 3 times: db_tool
Usage at stop: {'steps': 3, 'cost_units': 15, 'calls_in_window': 3, ...}
```

That's the same teaching pattern as Module 1's `DEFENSE` lines: not just
*blocked*, but **which** limit caught it and what the usage was at the moment it
tripped. Change `max_repeats` or the budget and a different control fires first —
worth trying, because in production you tune exactly these numbers.

Design note for real systems: limits should be **per identity** (user, session,
tenant), not global — otherwise one abusive session degrades everyone, which is
its own denial of service.
