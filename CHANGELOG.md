# Changelog

## v2.0.0 — 2026-10-04

First public release.

### Added
- **Place the Control**, a 15-minute playground that runs entirely in the browser
  (`lab/ui/play.html`, hosted at https://uddeshya-world.github.io/agentic-security-lab/).
  Four levels: watch the breach, stop three attacks on a 3-point budget, find the
  composition cut (MESA INV-01), and catch a tool whose description lies.
  Learner and Reviewer modes; Reviewer ends with questions to ask before
  approving an AI agent.
- Scenario 19 *MCP tool poisoning* (ASI04, LLM04:2026) with a manifest-pinning
  control (`defenses/m07/manifest_pin.py`).
- Reviewer track: three read-only scenarios for officials and approvers.
- Core labs 16 direct injection, 17 data guards, 18 agent identity.
- Site rebuilt on a shared component layer: path cards, lab cards, filter chips,
  stepper rail, checks rubric, trifecta HUD, pre-flight pane, scope gate,
  badge card. Playground is first in the nav.
- Server-side ledger of passed checks (`lab/ledger.py`).
- GitHub Pages workflow that publishes only the static playground and fails on
  any API route or network call.
- `LICENSE` (Apache-2.0), `NOTICE`, `SECURITY.md`, `CONTRIBUTING.md`.

### Changed
- OWASP mappings use the **2026** LLM Top 10 numbering throughout.
- Light theme retuned; motion limited to two speeds; contrast fixes so metadata
  text clears 4.5:1.

### Fixed
- **Completion badges could be forged.** The signing key was a constant shared by
  every install, and the transcript came from the browser. Each install now
  generates its own random key, and badges are built only from checks the server
  recorded as passed.
- CI now runs on `master`.

### Content
- AI & Agent Security: 23 scenarios (Core 9, Persistence 5, Operate 6,
  Reviewer 3), 49 graded checks.
- Blue Team / SOC: 4 scenarios, 6 graded checks (authoring; no credential yet).

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
