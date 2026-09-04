## Turn the pipeline on

Run in secure mode: the input and output scanners run over the same probe set,
and the harness computes the metrics.

The scanners catch:

- **input** — `ignore previous instructions`, `SYSTEM NOTE`, `filter=1=1`,
  `send … to …@` (prompt injection / jailbreak shapes);
- **output** — email addresses outside your owned domain (PII egress) and
  secret patterns like `sk-…` / `password:` (secret leakage).

This is **control C13 — a measured guardrail pipeline**. Because the scanners run
in well under a millisecond here, the lesson also shows how to keep the latency
budget honest: report p50/p95, and in production move expensive checks async or
apply them selectively so UX stays acceptable.
