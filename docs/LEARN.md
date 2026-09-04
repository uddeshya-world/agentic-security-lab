# Learn agent tool abuse in 30 minutes

**Primary path:** open the **catalog** and work the guided scenarios.  
You do **not** need host Python or host Ollama for Module 1 simulations.

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
| 0 | **L0** | Agent = planner + tools |
| 1 | **A1** | Tools alone are injectable (real SQL) |
| 2 | **A2** | How you poison the **LLM context** (RAG) |
| 3 | **A3** | Tool chain = impact (dump → email) |
| 4 | **A4** | **Exploit the agent**: RAG → compromised plan → executor → tools |
| 5 | **G1** | **Guardrail map**: what to build and where |

**A4 is the core “LLM was exploited” demo.**  
We inject a fixed plan that a prompt-injected model would emit (so class always works), then run it through the **real executor**. In secure mode you see **which guardrail** stops each step.

For each lesson:

1. Read the story  
2. **Run simulation**  
3. Read **SQL / plan / DEFENSE** lines  
4. Read takeaway  

## 4. Flip to secure mode

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
- Six control layers (lesson **G1**): RAG trust, plan validation, schema, least privilege, HITL, tool policy  
- How `SECURE_MODE` maps to each layer when you re-run **A4**  

## CLI alternative (optional)

Host Python still works for power users:

```text
pip install -r requirements.txt
python -m attacks.m01.attack_param_manipulation
# etc.
```

Prefer the **Lab Console** for teaching and demos.
