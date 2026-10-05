## Turn on provenance filtering

Open `rag/retriever.py`. In secure mode the retriever drops chunks whose
metadata marks them untrusted **before** they are returned:

```python
if is_secure():
    docs = [d for d in docs if d.metadata.get("trust") != "untrusted"]
```

This is **control C6 — RAG trust / provenance filter**. The poison never reaches
the planner, so there is nothing to obey.

The next step turns it on for one run with the mode switch above the timeline.
No rebuild is needed.

One honest caveat: in this lab the poisoned document arrives already labelled
`trust=untrusted`, so the filter has an easy job. In a real system nobody labels
the attacker's page for you. Provenance has to come from where the content was
collected (who wrote it, which source, whether the source lets the public edit),
and getting that right is most of the work.

> Important nuance for later: filtering at retrieval is **one** layer. If a
> poisoned chunk ever slips through, the executor and tool guardrails from the
> other scenarios must still hold. That defense-in-depth idea is the payoff of
> the full agent exploit scenario.
