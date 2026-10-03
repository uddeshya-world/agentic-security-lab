# OWASP / ASI coverage — what this lab teaches

> Generated from `lab/curriculum.py` + the `content/areas/` tree. Every number below is
> derived, not asserted: the *Covered* column is the module's own `covered` flag and the
> *Scenarios* column lists the folders whose `scenario.json` actually declares that id.

## Mission

Teach **AI agent security** as a practised skill, not a reading list:

- how agents are made to abuse their tools (excessive agency)
- how retrieval turns a document into an instruction (indirect prompt injection)
- how two harmless tools chain into an exfiltration
- how **controls outside the model** stop each one, and how you prove it

## OWASP LLM Top 10 for Applications (2026)

The list was renumbered on 4 Aug 2026. **Excessive Agency is LLM03** (was LLM06) and
**Hidden Context Exposure is LLM08** (was LLM07 System Prompt Leakage). Ids below are 2026;
`docs/AI-AGENT-SECURITY-CURRICULUM.md` holds the full 2025→2026 crosswalk.

| ID | Name | Covered | Scenarios that declare it |
|----|------|---------|---------------------------|
| LLM01 | Prompt Injection (direct & indirect) | **Yes** | `ai-security/02-rag-poisoning`, `ai-security/04-agent-exploit`, `ai-security/05-guardrail-map`, `ai-security/06-rag-deep-poisoning`, `ai-security/08-memory-poisoning`, `ai-security/09-guardrails`, `ai-security/10-redteam-pipeline`, `ai-security/13-prompt-leakage`, `ai-security/16-direct-injection` |
| LLM02 | Sensitive Information Disclosure | **Yes** | `ai-security/03-cross-tool-exfil`, `ai-security/05-guardrail-map`, `ai-security/09-guardrails`, `ai-security/10-redteam-pipeline`, `ai-security/17-data-guards`, `blue-team/00-orientation`, `blue-team/01-triage-the-exfil`, `blue-team/03-prove-the-control` |
| LLM03 | Excessive Agency | **Yes** | `ai-security/01-tool-abuse-sqli`, `ai-security/03-cross-tool-exfil`, `ai-security/04-agent-exploit`, `ai-security/05-guardrail-map`, `ai-security/10-redteam-pipeline`, `ai-security/12-governance`, `ai-security/16-direct-injection`, `ai-security/18-agent-identity`, `blue-team/01-triage-the-exfil`, `blue-team/02-write-the-detection` |
| LLM04 | Supply Chain | **Yes** | `ai-security/11-supply-chain` |
| LLM05 | Data and Model Poisoning | **Yes** | `ai-security/02-rag-poisoning`, `ai-security/06-rag-deep-poisoning`, `ai-security/14-grounding` |
| LLM06 | Unbounded Consumption | **Yes** | `ai-security/15-resource-limits` |
| LLM07 | Misinformation | **Yes** | `ai-security/14-grounding` |
| LLM08 | Hidden Context Exposure | **Yes** | `ai-security/13-prompt-leakage` |
| LLM09 | Vector and Embedding Weaknesses | **Yes** | `ai-security/02-rag-poisoning`, `ai-security/06-rag-deep-poisoning` |
| LLM10 | Improper Output Handling | **Yes** | `ai-security/09-guardrails`, `ai-security/17-data-guards` |

**Full: 10 · Partial: 0 · Not yet: 0** of 10

## OWASP Top 10 for Agentic Applications (ASI, 2026)

All ten are listed, including the ones this lab does **not** teach, so the denominator is
not self-selected.

| ID | Name | Covered | Scenarios that declare it |
|----|------|---------|---------------------------|
| ASI01 | Agent Goal Hijack | **Yes** | `ai-security/04-agent-exploit`, `ai-security/07-multi-agent`, `ai-security/08-memory-poisoning` |
| ASI02 | Tool Misuse and Exploitation | **Yes** | `ai-security/01-tool-abuse-sqli`, `ai-security/03-cross-tool-exfil`, `ai-security/04-agent-exploit`, `ai-security/05-guardrail-map` |
| ASI03 | Identity and Privilege Abuse | **Yes** | `ai-security/05-guardrail-map`, `ai-security/12-governance`, `ai-security/17-data-guards`, `ai-security/18-agent-identity` |
| ASI04 | Agentic Supply Chain Vulnerabilities | **Yes** | `ai-security/11-supply-chain` |
| ASI05 | Unexpected Code Execution (RCE) | No | — |
| ASI06 | Memory and Context Poisoning | **Yes** | `ai-security/02-rag-poisoning`, `ai-security/06-rag-deep-poisoning`, `ai-security/08-memory-poisoning` |
| ASI07 | Insecure Inter-Agent Communication | **Yes** | `ai-security/07-multi-agent` |
| ASI08 | Cascading Failures | No | — |
| ASI09 | Human-Agent Trust Exploitation | No | — |
| ASI10 | Rogue Agents | **Yes** | `ai-security/07-multi-agent`, `ai-security/11-supply-chain` |

**Full: 7 · Partial: 0 · Not yet: 3** of 10 (open: ASI05, ASI08, ASI09)

Controls taught: **21** (`C1`–`C21`, see `lab/curriculum.py::CONTROLS`).

## Where the learning actually happens

| Surface | Student activity |
|---------|------------------|
| Scenario stepper | Run the attack, then Check the evidence it left behind |
| Timeline + SQL evidence | See *how* the break works, hop by hop |
| `SECURE_MODE` flip | Re-run the same attack and watch a named control block it |
| Area page | Map every scenario to its OWASP / ASI ids and controls |
| Code pointers | Jump from a control to the file that implements it |
| Credential | Sign a transcript of graded checks the learner actually passed |

## What this lab is not

Coverage of a category means **one worked scenario**, not exhaustive treatment. Not taught
here: model supply-chain forensics, full NeMo / LLM Guard production pipelines, multi-agent
consensus attacks, and the three open ASI entries above. See `ROADMAP.md`.
