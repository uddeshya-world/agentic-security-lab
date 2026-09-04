# Writeup outline (post-ship community post)

**Title idea:** *DVWA for AI agents: measuring tool abuse before and after SECURE_MODE*

1. **Hook** — Coding agents with tools are a new attack surface (not just jailbreaks).
2. **Threat model** — Untrusted tool args, RAG as instruction channel, tool chaining for exfil.
3. **Lab design** — Local Docker, synthetic data, dual-mode tools, one env flag.
4. **Three attacks (Layer A)** — SQLi/path, poison retrieve, DB→email exfil. Show commands.
5. **Defenses** — Schema allow-list, least privilege, domain allow-list, trust-filtered RAG, simulated HITL.
6. **Metrics table** — Paste `before_after.md`.
7. **What this is not** — Not sandbox escape; not full multi-agent; not enterprise guardrails yet.
8. **Call to action** — Clone repo, run attack-01 both modes, file issues, roadmap modules 2–8.

Keep demos non-weaponized and local-only.
