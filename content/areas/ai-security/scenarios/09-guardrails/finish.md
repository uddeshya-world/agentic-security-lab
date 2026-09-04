## What you proved

- A guardrail layer is only a control if it's **measured**: catch rate,
  false-positive rate, and p50/p95 latency, benchmarked against a labeled set.
- **C13** scans both input (prompt injection / jailbreak) and output (PII egress,
  secret leakage), with the before/after delta as evidence.
- The engineering discipline — baseline, benchmark, latency budget — matters more
  than the specific detectors.

**Next:** *Red-team evaluation pipeline* — run every module's attack as a suite and
track attack-success rate over time.
