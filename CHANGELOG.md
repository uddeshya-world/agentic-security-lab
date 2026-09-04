# Changelog

## v1.1.0 — 2026-07-11

### Added
- **Lab Console** at `/lab/ui/` — browser-first guided lessons with live event log
- Lab APIs: `/lab/status`, `/lab/lessons`, `/lab/events`, `/lab/simulate/{id}`
- `docs/LEARN.md` 30-minute learning path
- README hero: open Lab Console first; Ollama clarified as internal/optional

### Learning product
- Simulations A1–A3 run inside the agent (no host Python required)
- Teaching cards: story, takeaway, design rule, OWASP, code paths
- MailHog link for exfil proof; secure-mode switch instructions in UI

## v1.0.0 — 2026-07-11

### Added
- Module 1 Layer A attacks: parameter manipulation, retrieval poisoning, cross-tool exfil
- Module 1 defenses under `SECURE_MODE`: schema validation, least privilege, simulated HITL, invoke timeout, RAG trust filter
- Metrics runner + `metrics/m01/results/before_after.md` generation
- Lab helper endpoints: `/lab/ingest-benign`, `/lab/ingest-poisoned`, `/lab/retrieve`
- Benign RAG auto-ingest on agent startup
- ROADMAP.md, FINDINGS-01, unit tests for defenses
- Localhost-only port binds in docker-compose

### Changed
- Honest README: planner + tool executor (not multi-agent / sandbox escape marketing)
- File tool secure jail uses `Path.relative_to`
- SECURITY_NOTES lists only implemented defenses

### Known stubs (not v1.0 features)
- NeMo / LLM Guard / OPA real backends
- Full Garak / DeepTeam / Promptfoo suites
- Modules 2–8
