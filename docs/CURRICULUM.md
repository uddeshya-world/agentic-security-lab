# CyberRange — Expert Curriculum Map

> Hands-on, browser-guided security training that runs on your own machine.
> Every path follows one pedagogy: **exploit it for real → build the control →
> measure the delta.** Mapped to certifications and to the jobs that pay for them.

This document is the full curriculum plan across all Areas. One Area — **AI &
Agent Security** — is built and shipping. The rest are planned here at expert
depth and authored as scenario folders over time. The build sequence is
deliberate: prove the format on the flagship, then scale content, never the
reverse.

---

## 1. Why this exists (positioning)

The interactive-lab space (Killercoda, TryHackMe, HTB Academy) is crowded on the
usual tracks and effectively owns Kubernetes/Linux certs. Competing there is a
losing game. Two things are *not* owned yet:

1. **AI / agent security.** There is no dominant hands-on curriculum and no
   dominant certification for securing LLM agents — the fastest-growing attack
   surface in the industry. This is the wedge.
2. **The attack→defend→measure loop as a first-class format.** Most labs teach
   *either* red team *or* blue team. Here every scenario makes you do both on the
   same system and produces a before/after number. That contrast is the lesson.

**Strategy:** own AI/agent security and the attack→defend pedagogy; use the
broader cyber Areas to make CyberRange a complete destination; publish the
flagship Area on existing platforms (e.g. Killercoda's scenario format) as a
*funnel* rather than fighting for cold traffic.

---

## 2. The Area model

Every Area is a catalog tile that answers three questions up front: **what you'll
do, which certification it maps to, and which job it prepares you for.**

```
Area  ─┬─ area.json         title · blurb · certs[] · roles[] · credential · env
       ├─ scenarios/        ordered, graded, hands-on paths
       └─ env/<area>/        the Area declares its OWN environment
```

**Invariant:** the lesson engine is environment-agnostic. Web AppSec needs a
vulnerable web app; malware analysis needs an isolated no-egress VM; DFIR needs
disk/memory images; cloud needs LocalStack. One stack cannot serve them, so the
environment is a property of the Area, and the engine only renders steps, runs
checks, and tracks progress.

Each scenario ends the same way: a **check that asserts real lab state** (did the
exfil land? did the guardrail fire? is the flag captured?), not a script's
exit code — the platform's technical differentiator.

---

## 3. Flagship — AI & Agent Security  **[SHIPPING — curriculum reconstructed 2026-09-05]**

The full agentic system (LangGraph planner + executor, SQL/email/file tools,
RAG, memory) — deliberately vulnerable, then hardened behind `SECURE_MODE`.

**Canonical syllabus:** [AI-AGENT-SECURITY-CURRICULUM.md](AI-AGENT-SECURITY-CURRICULUM.md)
(evidence from SANS SEC546/545/411, PortSwigger LLM path, 8kSec roadmap,
HTB AI Red Teamer, TryHackMe, Microsoft Learn, OWASP LLM 2026 + ASI 2026).

**Certs / frameworks:** OWASP Top 10 for LLM Applications **(2026)** · OWASP Top 10
for Agentic Applications **(2026)** · MITRE ATLAS.
**Roles:** AI Security Engineer · LLM/ML Red Teamer · AI AppSec · AI Platform
Security Architect.
**Native credential:** *AI Security Practitioner* — **Core track only**, not all labs.

### Core (required for the badge) — ~2.5 h

| # | Scenario | You learn |
|---|----------|-----------|
| A0 | What is an agent with tools? | data path and trust boundary |
| A1 | Tool abuse — SQL injection | tool schemas are a control surface |
| A2 | **Direct prompt injection** *(add)* | user-as-attacker, distinct from RAG |
| A3 | Poison the LLM context (RAG) | retrieved text becomes instructions |
| A4 | Cross-tool exfiltration | impact is a chain; side-effect tools need stronger gates |
| A5 | **Data guards / DLP** *(add)* | classify + mask/block on prompt, RAG, output, tool |
| A6 | **Agent identity / confused deputy** *(add)* | agent creds ≠ user; session is the principal |
| A7 | Exploit the agent end-to-end | RAG→planner→executor; defense in depth |
| A8 | Guardrail map *(rewrite)* | DLP + identity hops on the same drawing |

### Advanced — persistence · operate

Deep RAG, memory, multi-agent, MCP/supply chain, measured guardrails, red-team CI,
policy-as-code, hidden context (LLM08:2026), grounding, denial of wallet (LLM06:2026).

**Not this Area:** ASI05 RCE, ML privacy/evasion, browser/computer-use agents, MLOps platforms.

---

## 4. Roadmap Areas — planned at expert depth

Each Area below is authored as scenario folders when its turn comes, using the
same attack→defend→measure format and an Area-specific environment.

### 🕸️ Web Application Security
- **Env:** a deliberately-vulnerable web app + a proxy workflow.
- **Scenarios:** SQLi & NoSQLi · XSS (reflected/stored/DOM) · broken access
  control / IDOR · SSRF · authentication & session flaws · insecure
  deserialization · file-upload RCE. Each: exploit → patch the code → re-test.
- **Certs:** PortSwigger Web Security Academy · Burp Suite Certified Practitioner
  (BSCP) · eWPT.  **Roles:** AppSec Engineer · Web Pentester.

### 🎯 Offensive Security / Pentest
- **Env:** a target box (or small network) with a realistic foothold-to-root path.
- **Scenarios:** enumeration & recon · service exploitation · web-to-shell ·
  privilege escalation (Linux & Windows) · lateral movement · reporting.
- **Certs:** eJPT · PNPT · OSCP-prep.  **Roles:** Pentester · Red Teamer.

### 🛡️ Blue Team / SOC
- **Env:** log/telemetry corpus + a SIEM (e.g. OpenSearch/Elastic) preloaded with
  attack traces (including the AI-agent traces from the flagship Area).
- **Scenarios:** alert triage · log correlation · detection-rule authoring
  (Sigma) · threat hunting · writing the incident timeline.
- **Certs:** BTL1/BTL2 · GCIA-prep · Security+.  **Roles:** SOC Analyst ·
  Detection Engineer.

### ☁️ Cloud Security
- **Env:** LocalStack (AWS) + a Kubernetes-in-Docker cluster.
- **Scenarios:** IAM misconfiguration & privilege escalation · public
  bucket/secret exposure · container breakout · Kubernetes RBAC & network-policy
  hardening · workload identity.
- **Certs:** AWS Security Specialty · CKS-adjacent.  **Roles:** Cloud Security
  Engineer.

### 🔧 DevSecOps / Supply Chain
- **Env:** a CI/CD pipeline (Actions-style) with intentionally weak stages.
- **Scenarios:** leaked secrets in pipelines · dependency confusion / typosquat ·
  poisoned build step · IaC misconfig scanning · SBOM generation + verification.
- **Roles:** DevSecOps Engineer.

### 🔬 DFIR (Digital Forensics & Incident Response)
- **Env:** provided disk and memory images; no egress.
- **Scenarios:** memory triage (Volatility-style) · disk artifact analysis ·
  timeline reconstruction · ransomware IR playbook · producing the report.
- **Certs:** GCFA/GCIH-prep.  **Roles:** IR / Forensics Analyst.

### 🦠 Malware Analysis / Reverse Engineering
- **Env:** an **isolated, no-network** analysis container (safety-critical).
- **Scenarios:** static triage (strings, PE/ELF) · dynamic behavior in a sandbox
  · unpacking basics · IOC extraction · YARA-rule authoring.
- **Certs:** GREM-prep.  **Roles:** Malware Analyst.

### 🌐 Network & Fundamentals  *(the on-ramp)*
- **Env:** pcaps + a small multi-host topology.
- **Scenarios:** packet analysis (Wireshark-style) · protocol fundamentals ·
  common attacks on the wire · basic firewall/segmentation reasoning.
- **Certs:** Security+ · Network+.  **Roles:** Entry-level Analyst.

### 🔐 Cryptography & Secrets
- **Env:** small crypto services with real, exploitable mistakes.
- **Scenarios:** padding/oracle-style flaws · weak randomness · key-management
  failures · PKI/TLS validation mistakes · secret storage done right.
- **Roles:** AppSec · Platform Security.

### 📋 GRC / Policy-as-Code
- **Env:** OPA/Rego + a mock control catalog (reuses the flagship's governance
  module).
- **Scenarios:** encode a policy · map controls to NIST/ISO 27001 · gate actions
  by risk/blast-radius · build a queryable audit trail.
- **Roles:** GRC Analyst · Security Program Manager.

---

## 5. Career & credential layer

- Every Area page states **skills → job roles → industry certs** so learners see
  the payoff before starting.
- **Certificate of completion** is generated client-side on Area completion,
  downloadable and hash-verifiable — a credential hook without proctoring
  infrastructure. (Phase 2: accounts + a proctored/paid credential.)
- The flagship's **AI Security Practitioner** track is the original credential —
  filling the market gap where no dominant agentic-AI-security cert exists.

## 6. Delivery & business (free-first, staged monetization)

- **Now:** the open lab + guided UX + completion certificates are free. Growth
  comes from content — each scenario's `FINDINGS-*.md` is 80% of a blog post or
  video script — and from the open-source repo as a portfolio/credibility magnet.
- **Hosted (hybrid):** a public catalog + read-only lesson content + a canned
  demo at zero friction; real hands-on runs locally. The hosted surface ships
  none of the attack tooling by construction.
- **Phase 2:** accounts + progress persistence, a paid course tier, and a
  proctored certificate — layered on once the free funnel proves demand.

---

## 7. Build sequence (one-way ratchet)

1. **[done]** Content model + loaders; flagship Module 1 as scenario folders.
2. **[done]** Lesson engine: catalog / scenario / graded-check APIs; stepper UI;
   per-request `SECURE_MODE`; hosted-mode hardening.
3. **[next]** Terminal panel wired live (ttyd) + author flagship Modules 2–8.
4. **[later]** Second Area (Web AppSec — highest demand, clearest cert path).
5. **[later]** Accounts, persistence, paid tier, proctored credential.
