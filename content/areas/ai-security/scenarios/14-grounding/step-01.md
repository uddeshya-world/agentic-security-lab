## What this can and cannot check

Be clear about the boundary — it's the difference between a real control and
security theater:

| | |
|---|---|
| **Can check** | Is this claim supported by the retrieved sources? |
| **Cannot check** | Is this claim true in the world? |

A groundedness check is a **provenance** control, not a truth oracle. It catches:

1. **Fabrication** — the agent asserts a policy that appears in no source.
2. **Laundered poison** — the agent repeats a claim from a poisoned document as
   its own confident statement. Citation forces the bad source into view instead
   of letting the agent's authority hide it (this is where LLM09 meets the
   poisoning you did in Modules 2 and 6).

What it does **not** catch: a source that is itself wrong but legitimately
retrieved. That's a data-quality problem, and pretending otherwise would be
overclaiming.
