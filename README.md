# CyberRange

*(repository: `agentic-security-lab` — the engine keeps its original name)*

A deliberately vulnerable, **fully local** AI agent security lab — **"DVWA for AI agents."**  
Authorized security education and defensive research only.

**Local-only. Synthetic data. Fake credentials. Do not expose to the network.**

---

## New here? 15 minutes, nothing to install

Open **`lab/ui/play.html`** in a browser (or `/lab/ui/play.html` on a running
stack). *Place the Control* is a simulated, in-browser version of the lab:

1. **Watch the breach** — a public help-article edit steers a helpdesk agent into
   emailing applicant records, hop by hop.
2. **Place the controls** — three attacks, a budget of 3 points, find the
   cheapest set of controls that stops all of them.
3. **Find the composition cut** — three agents that each pass alone leak together;
   pick the one policy that breaks the trifecta without breaking the service
   (MESA invariant INV-01).

No model runs on that page and every record is synthetic, which is why it is
safe to host publicly. Everything below is the real lab it previews.

---

## Start here — guided, hands-on paths

```text
docker compose up -d
```

Open the **catalog** (Killercoda-style, guided, step-verified):

### 👉 http://127.0.0.1:8000/  (Areas catalog → guided scenarios)

Pick the **AI & Agent Security** area and start at *What is an agent with tools?*.
Each scenario is a stepped lesson beside a live console. **Run** fires the attack
against the real tools and fills the timeline; **Check** then asserts what the run
left behind — dumped rows, a message in the mail sink, the specific guardrail that
fired. Check never runs the attack for you, so a step cannot be completed without
doing the work. Flip the run's mode to secure and prove the same payload is
stopped.

Finish every graded check in the Area to claim a **lab completion badge**: an
HMAC-signed transcript of exactly which checks you passed and in which mode. It is
signed by your own instance, so it is tamper-evident, not third-party attested —
`/lab/ui/verify.html` says so on the badge itself.

Optional in-browser terminal (local only):

```text
docker compose -f docker-compose.yml -f docker-compose.terminal.yml up -d ttyd
```

The **classic single-page console** (fire an attack, read the timeline) is still
at **http://127.0.0.1:8000/lab/ui/**.

The full curriculum plan — flagship modules plus the broader cyber Areas (Web
AppSec, Offensive, Blue Team, Cloud, DevSecOps, DFIR, Malware RE, Network,
Crypto, GRC), each mapped to certs and jobs — is in
[docs/CURRICULUM.md](docs/CURRICULUM.md).

Why Docker? This is a **real agent stack** (planner + tools + RAG + mail sink), not an HTML mock.

### Public / hosted demo (safe by construction)

```text
docker compose -f docker-compose.hosted.yml up -d
```

Serves only the catalog + read-only lesson content. Ships **no** tool servers,
Ollama, MailHog, or terminal, and `LAB_HOSTED=1` removes the attack routes
(`/run`, `/lab/attack`, graded checks, ingestion) from the app. The attack path
exists only in the local stack above.

### Ollama (required for live attacks)

- Runs **inside** compose (`ollama` service). Host `:11434` is closed on purpose.
- Agent reaches it at `http://ollama:11434`. Model: `qwen2.5:3b-instruct` (or `OLLAMA_MODEL`).
- Live attacks need Ollama healthy (console shows **ollama** pill green).

Deterministic teaching sims still exist at `POST /lab/simulate/{id}` for CI / no-LLM demos.
---

## Status

| Module | Topic | Status |
|--------|--------|--------|
| **0** | Foundation: planner + tools + RAG + memory | Done |
| **1** | Tool abuse — attacks, defenses, metrics, **Lab Console + guided paths** | Done (v1.2 lesson engine) |
| 2–8 | RAG poisoning, multi-agent, memory, guardrails, red-team CI, supply chain, governance | Built at lab scale (deterministic sims + graded scenarios) — see [ROADMAP.md](ROADMAP.md) |
| — | Blue Team / SOC Area | Authoring (4 scenarios, credential not issuable yet) |

Architecture: **planner (LLM) → tool executor → HTTP tools** (not multi-agent sandbox escape).

## Safety

- Ports bound to **127.0.0.1** only.
- **DO NOT** expose this stack to the internet.

## Setup

Prerequisites: Docker Desktop. Host Python optional (CLI attacks only).

```text
cp .env.example .env
docker compose up -d
# open http://127.0.0.1:8000/lab/ui/
```

PowerShell / scripts: `.\run.ps1 -Cmd up` then open the console URL.

### Secure vs vulnerable mode

```powershell
# Vulnerable (attacks succeed)
$env:SECURE_MODE="false"
docker compose up -d --force-recreate agent db-tool email-tool file-tool

# Secure (attacks blocked)
$env:SECURE_MODE="true"
docker compose up -d --force-recreate agent db-tool email-tool file-tool
```

Refresh Lab Console and re-run simulations.

### CLI / metrics (optional)

```text
pip install -r requirements.txt
./run.sh attack-01
./run.sh metrics-01
```

## What you learn (AI security curriculum)

1. **Attack** agent tools (SQLi, path, exfil) and **indirect prompt injection** via RAG  
2. **Map** each demo to **OWASP LLM Top 10** + Agentic ASI (in UI + docs)  
3. **Remediate**: schema validation, least privilege, HITL, domain allow-lists, RAG trust filters  
4. **Prove** controls with `SECURE_MODE` before/after  

| Doc | Purpose |
|-----|---------|
| [docs/REMEDIATION.md](docs/REMEDIATION.md) | How to stop each attack |
| [docs/OWASP_COVERAGE.md](docs/OWASP_COVERAGE.md) | What’s covered / not covered |
| [docs/LEARN.md](docs/LEARN.md) | Core path (~2.5 hours) |
| [SECURITY_NOTES.md](SECURITY_NOTES.md) | Weakness inventory |
| `GET /lab/curriculum` | Machine-readable map |

**Blue-team loop in the UI:** Fire attack → read **Remediation** panel → enable SECURE_MODE → re-fire → match DEFENSE lines to controls C1–C7.

## Repo map

- `lab/ui/` — Lab Console  
- `lab/simulate.py` — guided simulations + event log  
- `attacks/m01/` — CLI attack scripts  
- `defenses/m01/` — secure-mode controls  
- `docs/LEARN.md` — Core path (~2.5 hours)  
- `lab/ui/play.html` — 15-minute in-browser preview (no Docker)  
