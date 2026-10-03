## What you proved

- Retrieved documents enter the model in the same slot as trusted context, so
  the model obeys them — **indirect prompt injection (LLM01)**.
- A benign question is enough to pull attacker instructions into context if the
  corpus is poisoned (**LLM05 / LLM09 / ASI06** in the 2026 numbering).
- **Control C6** (trust/provenance filtering) drops untrusted chunks at
  retrieval time — the poison never reaches the planner.
- Filtering RAG is necessary but not sufficient; downstream guardrails must still
  hold if a chunk slips through.

**Next:** *Cross-tool exfiltration* — the payload the poison was trying to
trigger: dump data with one tool, send it out with another.
