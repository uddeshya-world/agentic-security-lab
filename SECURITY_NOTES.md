# Security Notes -- Intentional Weaknesses

This is a **deliberately vulnerable** lab for authorized security education
and defensive research. Every weakness below is intentional, documented, and
(where Module 1 applies) toggled off behind `SECURE_MODE=true`.

**DO NOT deploy this anywhere reachable by untrusted users or networks.**
Compose binds service ports to `127.0.0.1` only. Local-only, synthetic data,
fake credentials throughout.

## Weakness -> OWASP mapping

| # | Weakness | Location | OWASP LLM Top 10 (2026) | OWASP Agentic ASI (2026) |
|---|---|---|---|---|
| 1 | Tools execute with broad privileges, no approval gate | `tools/*/server.py`, `agents/executor.py` | LLM03 Excessive Agency | ASI02 Tool Misuse, ASI03 Privilege Abuse |
| 2 | Permissive tool schemas; db tool concatenates raw SQL fragment | `tools/db_tool/queries.py::query_vulnerable` | LLM03, LLM02 | ASI02 |
| 3 | File tool joins path naively (path traversal) | `tools/file_tool/server.py::_resolve_vulnerable` | LLM03 | ASI02 |
| 4 | Email tool: no recipient allow-list | `tools/email_tool/server.py` | LLM02 | ASI02 |
| 5 | RAG retrieves top-k with no trust checks | `rag/retriever.py`, planner prompt | LLM09, LLM05, LLM01 | ASI01, ASI06 |
| 6 | Planner and executor fully trust each other | `agents/planner.py`, `agents/executor.py` | LLM01, LLM03 | ASI07, ASI01 |
| 7 | Memory writes unvalidated | `memory/store.py`, `agents/graph.py` | LLM02 | ASI06 |
| 8 | Guardrails / OPA seams are no-op or unused for real policy | `guardrails/`, `policy/opa_seam.py` | LLM10, LLM06 | ASI08, ASI09 |

_Exact OWASP category numbering/names spot-checked against the live OWASP
Gen AI Security Project pages as of build time; frameworks evolve._

## Module 1 defenses (`SECURE_MODE=true`)

Implemented and wired:

| Defense | Location | What it does |
|---------|----------|--------------|
| Schema validation | `defenses/m01/schema_validation.py` | Allow-listed tools/args; rejects unscoped db `filter` / `..` paths at executor |
| Least privilege | `defenses/m01/least_privilege.py` + tool secure branches | Parameterized `customer_id` db access; file jail; email domain `example.test` |
| Simulated HITL approval | `defenses/m01/approval_gate.py` | Denies email + file write unless `LAB_APPROVE=1` (agent path) |
| Invoke timeout isolation | `defenses/m01/isolation.py` | Timeout wrapper only — **not** container sandbox escape prevention |
| RAG trust filter | `rag/retriever.py` | Drops chunks with `trust=untrusted` metadata |
| Tool secure branches | `tools/db_tool`, `file_tool`, `email_tool` | Layer-A (direct HTTP) blocks for SQLi, traversal, external email |

Toggle: `SECURE_MODE=true` (read via `defenses/config.py` and `tools.base.is_secure`).  
**Recreate containers** after changing the env var so all services pick it up:

```text
SECURE_MODE=true docker compose up -d --force-recreate agent db-tool email-tool file-tool
```

## Seams not fully implemented (see ROADMAP.md)

- `policy/opa_seam.py` — always-allow stub; real OPA/Rego in a future module.
- `guardrails/nemo_seam.py`, `guardrails/llmguard_seam.py` — no-op passthrough.
- `redteam/*` — wiring/smoke only, not a full red-team suite.

## Safety packaging

- Ports published as `127.0.0.1:<port>` only.
- Synthetic DB (`alice@example.test`, etc.), fake Langfuse keys in `.env.example`.
- Poison corpus is **not** auto-ingested; attack scripts / `/lab/ingest-poisoned` load it.
- Do not run this stack on a VPS or shared LAN without additional network controls.
