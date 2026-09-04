# Roadmap (post v1.0)

**v1.0 scope:** Module 0 foundation + Module 1 tool abuse (prove → defend → measure).  
Everything below is **not** implemented. Do not treat folder seams as finished features.

| Module | Topic | Status |
|--------|--------|--------|
| 0 | Foundation (agent, tools, RAG, memory, OTel seams) | **In v1.0** |
| 1 | Tool abuse & insecure tool servers | **In v1.0** |
| 2 | RAG poisoning & retrieval attacks (crowding + false provenance) | **Built** (guided scenario + deterministic sim) |
| 3 | Multi-agent / orchestrator attacks (tampering + rogue agent) | **Built** |
| 4 | State, memory & long-running poisoning | **Built** |
| 5 | Production guardrails & observability (measured pipeline) | **Built** |
| 6 | Red-team evaluation pipeline (battery + CI regression) | **Built** |
| 7 | Supply chain security for agents (attestation) | **Built** |
| 8 | Governance, policy-as-code, HITL, audit trail | **Built** |

Modules 2-8 are lab-scale, deterministic implementations wired into the guided
lesson engine as scenarios 06-12 (`content/areas/ai-security/scenarios/`), each
with real attack → defend → measure and self-grading checks. Simulations live in
`lab/sims_advanced.py`; defenses in `defenses/m0X/`, `guardrails/pipeline.py`,
`policy/engine.py`. The full curriculum across all cyber Areas is in
[docs/CURRICULUM.md](docs/CURRICULUM.md).

Curriculum prompts (if present one level up): `Agentic-Security-Lab-ClaudeCode-Prompts.md`.

**North star for v1.0:** a stranger can clone, run attacks under `SECURE_MODE=false`, re-run under `SECURE_MODE=true`, and get a before/after metrics table.
