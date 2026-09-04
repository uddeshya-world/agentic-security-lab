# OWASP / ASI coverage — what this lab teaches

## Mission

Educate on **AI agent security** (not generic web CTF only):

- How agents abuse tools (excessive agency)  
- How RAG enables **indirect prompt injection**  
- How multi-tool chains exfiltrate data  
- How **defense-in-depth outside the model** remediates  

## OWASP LLM Top 10 (2025) — coverage

| ID | Name | Covered? | Lab attacks / modules |
|----|------|----------|------------------------|
| LLM01 | Prompt Injection | **Yes** | `indirect_pi`, A2, A4 |
| LLM02 | Sensitive Information Disclosure | **Yes** | `direct_sqli`, `exfil_chain`, A3 |
| LLM03 | Supply Chain | No | Roadmap M7 |
| LLM04 | Data and Model Poisoning | **Yes** | poisoned RAG corpus |
| LLM05 | Improper Output Handling | Partial | guardrail seams only |
| LLM06 | Excessive Agency | **Yes** | all tool attacks |
| LLM07 | System Prompt Leakage | No | — |
| LLM08 | Vector / Embedding Weaknesses | **Yes** | retrieval of poison |
| LLM09 | Misinformation | No | — |
| LLM10 | Unbounded Consumption | Partial | `MAX_PLAN_STEPS` |

**Full: 5 · Partial: 2 · Not yet: 3** of 10

## OWASP Agentic (ASI) themes covered

| ID | Name | Covered? |
|----|------|----------|
| ASI01 | Agent Goal Hijack | **Yes** (PI / poison) |
| ASI02 | Tool Misuse | **Yes** |
| ASI03 | Privilege Abuse | Partial (unscoped DB) |
| ASI06 | Memory/Context Poisoning | **Yes** (RAG) |
| ASI07 | Insecure inter-agent trust | Partial (planner→executor) |

## Where AI security education happens in the product

| Surface | Student activity |
|---------|------------------|
| Lab Console attack catalog | Fire real/fallback agent exploits |
| Timeline + SQL evidence | See *how* the break works |
| Remediation panel | Learn *how to stop* it |
| OWASP coverage panel | Map to industry taxonomy |
| `SECURE_MODE` toggle | Prove controls work (before/after) |
| Code pointers | Map control → file in the repo |

## Intentionally not the whole of AI security

This lab is **Module 0–1 depth**: agent tools + RAG + basic guardrails.  
Not yet: multi-agent consensus attacks, full NeMo/LLM Guard pipelines, model supply chain, jailbreak eval suites (see ROADMAP).
