In Module 1 you defended RAG by dropping chunks whose metadata said
`trust=untrusted`. A real attacker doesn't fill in that label honestly. This
module breaks the metadata filter two ways and forces a better defense:

- **False provenance** — the poison doc is tagged `trust=seed`, so the metadata
  filter waves it straight through.
- **Embedding-space crowding** — the corpus is flooded with near-duplicate poison
  chunks stuffed with the target query's keywords, so they dominate top-k.

The fix isn't a better label; it's looking at the **content**: retrieved
documents should never contain instructions aimed at the agent, and a flood of
near-identical chunks is itself a signal.
