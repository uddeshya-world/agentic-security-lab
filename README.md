# CyberRange

*(repository: `agentic-security-lab` — the engine keeps its original name)*

A deliberately vulnerable, **fully local** AI agent security lab — **"DVWA for AI agents."**  
Authorized security education and defensive research only.

**Local-only. Synthetic data. Fake credentials. Do not expose to the network.**

---

## New here? 15 minutes, nothing to install

**Play it in your browser: https://uddeshya-world.github.io/agentic-security-lab/**
(or open `lab/ui/play.html`, or `/lab/ui/play.html` on a running stack).

![Place the Control: level 1 breach, level 2 budget, level 3 composition cut](docs/media/place-the-control.gif)

*Place the Control* is a simulated, in-browser version of the lab.
Everyone teaches you to break the agent. Here you decide where the control goes.

1. **Watch the breach**: a public help-article edit steers a helpdesk agent into
   emailing applicant records, hop by hop.
2. **Place the controls**: three attacks, a budget of 3 points, find the
   cheapest set of controls that stops all of them.
3. **Find the composition cut**: three agents that each pass alone leak together;
   pick the one policy that breaks the trifecta without breaking the service
   (MESA invariant INV-01).
4. **The tool lies**: a registry tool's description tells the agent to email
   lookups out. Two cuts hold; the debrief explains why you want both.

A **Reviewer** switch rewrites the copy for officials and approvers and turns the
result into a printable list of questions to ask before approving an AI agent.

No model runs on that page and every record is synthetic, which is why it is
safe to host publicly. Everything below is the real lab it previews.

---

## Watch first: the Core path in 9 short videos

Each Core scenario has an explainer of about 80 seconds: one everyday analogy, the
real lab running on synthetic data, and the point where the analogy stops being true.
The same video opens from the **Watch** button at the top of each lesson.

[![Tool abuse: SQL injection, explainer video](https://uddeshya-world.github.io/agentic-security-lab/video/01-tool-abuse-sqli-thumb.png)](https://uddeshya-world.github.io/agentic-security-lab/video/01-tool-abuse-sqli.mp4)

| # | Video | Analogy | Length |
|---|---|---|---|
| 1 | [What is an agent with tools?](https://uddeshya-world.github.io/agentic-security-lab/video/00-orientation.mp4) | an office assistant and a clerk | 1:20 |
| 2 | [Tool abuse: SQL injection](https://uddeshya-world.github.io/agentic-security-lab/video/01-tool-abuse-sqli.mp4) | a library request slip | 1:25 |
| 3 | [Direct prompt injection](https://uddeshya-world.github.io/agentic-security-lab/video/16-direct-injection.mp4) | a bank teller and the vault | 1:20 |
| 4 | [Poison the LLM context (RAG)](https://uddeshya-world.github.io/agentic-security-lab/video/02-rag-poisoning.mp4) | a forged page in the handbook | 1:25 |
| 5 | [Cross-tool exfiltration](https://uddeshya-world.github.io/agentic-security-lab/video/03-cross-tool-exfil.mp4) | the post room | 1:26 |
| 6 | [Data guards (DLP)](https://uddeshya-world.github.io/agentic-security-lab/video/17-data-guards.mp4) | airport security | 1:26 |
| 7 | [Agent identity and the confused deputy](https://uddeshya-world.github.io/agentic-security-lab/video/18-agent-identity.mp4) | a valet key | 1:20 |
| 8 | [Exploit the agent end to end](https://uddeshya-world.github.io/agentic-security-lab/video/04-agent-exploit.mp4) | a heist and a bank's doors | 1:30 |
| 9 | [Guardrail map](https://uddeshya-world.github.io/agentic-security-lab/video/05-guardrail-map.mp4) | a building fire plan | 1:15 |

Captions are burned in; transcripts are in [`lab/ui/video/`](lab/ui/video/). Scripts and
the rebuild pipeline: [`docs/video/`](docs/video/). Files and checksums: the
[`videos-v1` release](https://github.com/uddeshya-world/agentic-security-lab/releases/tag/videos-v1).

---

## Start here — guided, hands-on paths

**New student? Follow the [student guide](docs/LEARN.md)**: what to install, how a
lesson works, the Core order, claiming the badge, and fixes for common problems.

The short version. You need Docker (see [Setup](#setup)). Then:

```text
git clone https://github.com/uddeshya-world/agentic-security-lab.git
cd agentic-security-lab
docker compose up -d
```

The first start downloads images and a small local model, so give it a few
minutes. Then open the **catalog** (Killercoda-style, guided, step-verified):

### 👉 http://127.0.0.1:8000/  (Areas catalog → guided scenarios)

Pick the **AI & Agent Security** area and start at *What is an agent with tools?*.
Each scenario is a stepped lesson beside a live console. **Run** fires the attack
against the real tools and fills the timeline; **Check** then asserts what the run
left behind — dumped rows, a message in the mail sink, the specific guardrail that
fired. Check never runs the attack for you, so a step cannot be completed without
doing the work. Flip the run's mode to secure and prove the same payload is
stopped.

Finish the **Core path** (9 scenarios, 23 graded checks) to claim the **AI Security
Practitioner completion badge**: an HMAC-signed transcript of exactly which checks
you passed and in which mode, with an optional name you type in. It is
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

### Ollama (only for live attacks and chat)

- Graded steps never need it. Every scenario's Run and Check are deterministic.
- Runs **inside** compose (`ollama` service). Host `:11434` is closed on purpose.
- Agent reaches it at `http://ollama:11434`. Default model: `qwen2.5:1.5b-instruct` (set `OLLAMA_MODEL` to change it).
- Live attacks and the sandbox chat need Ollama healthy (console shows **ollama** pill green). On a CPU-only machine a live call can take minutes.

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

Prerequisites:

- **Windows or macOS:** Docker Desktop.
- **Linux:** Docker Engine with the Compose plugin (`docker compose version` should work). If every tool shows "timed out" on the status panel, containers cannot reach each other: check the host firewall (an iptables `FORWARD` policy of `DROP` blocks Docker's bridge network).
- Host Python is optional (CLI attacks only).
- Clone outside a synced folder (OneDrive, Dropbox) if you can. The agent mounts the source folder, and sync clients slow its start-up a lot.

```text
cp .env.example .env    # optional: every setting has a default
docker compose up -d
# open http://127.0.0.1:8000/
```

PowerShell / scripts: `.\run.ps1 -Cmd up` then open the console URL.

### Secure vs vulnerable mode

Guided scenarios switch the mode for one run with the switch above the timeline,
and graded steps pick the right mode for you. Nothing below is needed to finish a
scenario. To harden the long-running tool servers persistently instead:

```bash
# Vulnerable (attacks succeed)
SECURE_MODE=false docker compose up -d --force-recreate agent db-tool email-tool file-tool

# Secure (attacks blocked)
SECURE_MODE=true docker compose up -d --force-recreate agent db-tool email-tool file-tool
```

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
| [docs/LEARN.md](docs/LEARN.md) | Student guide: start here (Core path, ~2.5 hours, badge) |
| [SECURITY_NOTES.md](SECURITY_NOTES.md) | Weakness inventory |
| `GET /lab/curriculum` | Machine-readable map |

**Blue-team loop in the UI:** Fire attack → read **Remediation** panel → enable SECURE_MODE → re-fire → match DEFENSE lines to controls C1–C7.

## Repo map

- `lab/ui/` — Lab Console  
- `lab/simulate.py` — guided simulations + event log  
- `attacks/m01/` — CLI attack scripts  
- `defenses/m01/` — secure-mode controls  
- `docs/LEARN.md`: student guide, start here (Core path, ~2.5 hours, badge)  
- `lab/ui/play.html` — 15-minute in-browser preview (no Docker)  

## Contributing and security

- [CONTRIBUTING.md](CONTRIBUTING.md): how to add a scenario and what the tests guard
- [SECURITY.md](SECURITY.md): which weaknesses are intentional, and how to report one that isn't

## License

[Apache License 2.0](LICENSE). Copyright 2026 Uddeshya Kumar. See [NOTICE](NOTICE).
