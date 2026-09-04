## Turn on provenance filtering

Open `rag/retriever.py`. In secure mode the retriever drops chunks whose
metadata marks them untrusted **before** they are returned:

```python
if is_secure():
    docs = [d for d in docs if d.metadata.get("trust") != "untrusted"]
```

This is **control C6 — RAG trust / provenance filter**. The poison never reaches
the planner, so there is nothing to obey.

Set the mode switch above the timeline to **secure** and press **Run** — that
forces the control on for this run only, with no rebuild. To harden the
long-running tool servers persistently instead, recreate the stack:

```bash
SECURE_MODE=true docker compose up -d --force-recreate agent db-tool email-tool file-tool
```

> Important nuance for later: filtering at retrieval is **one** layer. If a
> poisoned chunk ever slips through, the executor and tool guardrails from the
> other scenarios must still hold. That defense-in-depth idea is the payoff of
> scenario A4.
