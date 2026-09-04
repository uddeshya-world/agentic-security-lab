## What you proved

- Long-term memory is an input channel that **persists across sessions**, so a
  single poisoned write becomes a standing backdoor (**ASI06**).
- **C11** (write validation) keeps agent-directed instructions out of the store;
  **C12** (provenance signing) quarantines unsigned or tampered entries on recall.
- Defense in depth: stopped at write, and caught at read even on a direct DB write.

**Next:** *Guardrails & observability* — turn ad-hoc defenses into a measured
pipeline with catch-rate and latency numbers.
