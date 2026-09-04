## Read the effectiveness numbers

Open the **Forensics** panel after the secure run — the evidence carries the full
dashboard:

```
catch_rate, false_positive_rate, true/false positives/negatives, p50/p95 latency
```

The **Check** passes when the pipeline catches at least 80% of attacks while
keeping false positives at or below 20% — a real bar, not a toy pass/fail.

That's the deliverable enterprises pay for: not "we have guardrails," but "our
guardrails catch X% of attacks, block Y% of legitimate traffic, and add Z ms at
p95." Numbers you can defend, track over time, and alert on when they regress.
