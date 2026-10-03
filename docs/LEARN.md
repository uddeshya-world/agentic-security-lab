# Learn AI & Agent Security — Core path (~2.5 hours)

**Primary path:** open the **catalog** and work the **Core** track (badge).  
**Never touched agent security?** Play `/lab/ui/play.html` first — 15 minutes, simulated, no Docker.  
You do **not** need host Python or host Ollama for graded simulations.

## 1. Start the lab

```text
cd agentic-security-lab
cp .env.example .env   # once
docker compose up -d
```

Wait until tools and agent are healthy, then open:

**http://127.0.0.1:8000/** — redirects to the catalog (`/lab/ui/catalog.html`).

The **sandbox console** at `/lab/ui/index.html` is the free-fire surface: the whole
attack catalogue against the live agent, no steps and no grading. Use the catalog
to learn, the console to experiment.

### Ollama confusion (read this once)

| Question | Answer |
|----------|--------|
| Is Ollama required for lessons A1–A3? | **No** |
| Why isn’t `localhost:11434` open? | Ollama stays **inside** Docker; only the agent talks to it |
| When do I need Ollama? | Only the optional live-agent runs in the sandbox console |

## 2. Two things are called "secure mode"

| | What it is | Where |
|---|---|---|
| **Per run** | Forces the control on for one run. Nothing rebuilds, nothing persists. | The mode switch above the timeline in a scenario |
| **Persistent** | Recreates the containers so the long-running tool servers are hardened too. | `SECURE_MODE=true docker compose up -d --force-recreate agent db-tool email-tool file-tool` |

Graded steps use the per-run switch, and a step's check states which mode it
grades. You do not need the container recreate to finish any scenario.

## 3. Run lessons (in order)

| # | Lesson | What you learn |
|---|--------|----------------|
| A0 | Orientation | Agent = planner + tools; trust boundary |
| A1 | Tool SQLi | Tools alone are injectable (real SQL) |
| A2 | Direct prompt injection | User chat steers the planner (LLM01) |
| A3 | RAG poison | Retrieved docs become instructions |
| A4 | Cross-tool exfil | Dump → email; MailHog is the incident |
| A5 | Data guards / DLP | Classify + mask/block on four channels |
| A6 | Agent identity | Session principal, not the model's args |
| A7 | Full agent exploit | Poison → plan → executor → tools |
| A8 | Guardrail map | DLP + identity on the drawing — then claim the badge |

Advanced tracks (persistence, operate) are optional after Core.

**A7 is the core “LLM was exploited” demo.**  
We inject a fixed plan that a prompt-injected model would emit (so class always works), then run it through the **real executor**. In secure mode you see **which guardrail** stops each step.

For each lesson:

1. Read the step  
2. **Run** — this performs the attack against the real tools  
3. Read the **SQL / plan / DEFENSE** lines it produced  
4. **Check** — this asserts the evidence the run left behind  
5. Read the takeaway  

**Run and Check are two different buttons and the order matters.** Check never performs
the attack; it only looks for what the attack left in the lab (dumped rows, a message in
MailHog, the named control that fired). No run, no pass.

## 4. Flip to secure mode persistently (optional)

**You do not need this to finish any scenario.** Graded steps use the per-run mode switch
from section 2. Do this only if you want the long-running tool servers hardened too — for
example to confirm a control holds outside the graded path.

From the lab folder:

```powershell
$env:SECURE_MODE="true"
docker compose up -d --force-recreate agent db-tool email-tool file-tool
```

Refresh Lab Console → badge should show secure → re-run A1–A3 → expect **BLOCKED**.

Back to vulnerable:

```powershell
$env:SECURE_MODE="false"
docker compose up -d --force-recreate agent db-tool email-tool file-tool
```

## 5. What you should be able to explain after

- How an attacker exploits the **agent** (RAG poison → malicious plan → tools), not only raw tools  
- Why “just secure the LLM” is incomplete — **guardrails outside the model**  
- The **eight hops** on the agent data path (lesson **A8**, `05-guardrail-map`) and the control on each: input DLP, RAG + context DLP, planner output, identity, schema, least privilege, tool DLP + HITL + egress, output DLP  
- How `SECURE_MODE` maps to each hop when you re-run **A7** (the full chain)  

## CLI alternative (optional)

Host Python still works for power users:

```text
pip install -r requirements.txt
python -m attacks.m01.attack_param_manipulation
# etc.
```

Prefer the **Lab Console** for teaching and demos.
