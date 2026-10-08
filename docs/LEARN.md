# Student guide: start here

This guide takes you from nothing installed to the **AI Security Practitioner
completion badge**. The badge path is the **Core path**: 9 scenarios, 23 graded
checks, about 2.5 hours (the lessons estimate 146 minutes), plus setup.

Everything runs on your own machine. The agent, its tools, the database and the mail
inbox are all local, and every record in them is synthetic.

> **Rules of the range.** Use these techniques only on this lab, or on systems you
> have written permission to test. The lab is built for learning and defensive
> research.

---

## 0. Not sure yet? Try the 15-minute version first

**https://uddeshya-world.github.io/agentic-security-lab/**

*Place the Control* runs in your browser with nothing to install. It is simulated,
so nothing is graded and there is no badge, but it shows what the full lab is about.
Skip it if you already know you want the real thing.

---

## 1. What you need

| You need | Notes |
|---|---|
| **Docker** | Windows or macOS: [Docker Desktop](https://www.docker.com/products/docker-desktop/), started before you begin. Linux: Docker Engine with the Compose plugin; `docker compose version` should print a version. |
| **Git** | To clone the lab. |
| **A web browser** | Chrome, Edge or Firefox. |
| **Internet** | For the first start (it downloads images and a small local model) and for the explainer videos. The lessons themselves run offline. |

You do **not** need Python, an API key, a GPU or any cloud account. Graded steps never
call the AI model, so a slow laptop is fine.

---

## 2. Start the lab (about 10 minutes the first time)

Open a terminal (PowerShell on Windows) in a normal folder. **Avoid OneDrive, Dropbox
or other synced folders**: the lab mounts its folder, and sync clients make start-up
much slower. `C:\labs\` or `~/labs/` is a good place.

```text
git clone https://github.com/uddeshya-world/agentic-security-lab.git
cd agentic-security-lab
docker compose up -d
```

The first start downloads several images and a small local model, so it takes a few
minutes. Later starts are much faster.

Then open **http://127.0.0.1:8000/** in your browser. You should see the CyberRange
catalog. If the page does not load yet, wait a minute and refresh.

> Setting files are optional. Every setting has a default, so you do not need to copy
> `.env.example` to `.env` unless you want to change something.

---

## 3. Find the Core path

1. On the catalog, open **AI & Agent Security**.
2. The Area page lists the paths. **Core path** is marked *required for the badge*.
3. Start with the first scenario, **What is an agent with tools?**, and go in this order:

| # | Scenario | Time | What it teaches |
|---|---|---|---|
| 1 | What is an agent with tools? | 8 min | The executor is the trust boundary, because the planner can be lied to. |
| 2 | Tool abuse: SQL injection (no LLM needed) | 15 min | If a tool lets the caller write part of the query, any caller can take everything. |
| 3 | Direct prompt injection & jailbreak | 15 min | A model can be talked into anything, so the rule has to live in the tool. |
| 4 | Poison the LLM context (RAG) | 15 min | Anything the agent reads can carry instructions. |
| 5 | Cross-tool exfiltration (dump → email) | 18 min | Reading data is a problem; sending it out is the breach. |
| 6 | Data guards: DLP for agents | 20 min | An allow-list checks where data goes; DLP checks what the data is. |
| 7 | Agent identity & confused deputy | 15 min | The session decides whose data the agent may touch, never the model. |
| 8 | Exploit the agent (RAG → planner → tools) | 25 min | Defense in depth: one failure is not a breach. |
| 9 | Guardrail map: what to build and where | 15 min | A control on every hop from question to data leaving. |

The other paths (Persistence, Operate, Reviewer) are optional and can wait until after
the badge.

---

## 4. How a lesson works

### The first time: two boxes to tick

Before your first scenario, a short page explains what the range is and is not. Tick
both boxes (synthetic, local targets; you run this instance yourself) and press
**Start**.

### Watch first (about 80 seconds)

Each Core lesson opens with an **In plain terms** box: one everyday analogy, and the
point where the analogy stops being true. Press **▶ Watch the explainer** for the
matching short video. It streams from GitHub Pages only when you press it, has
captions built in, and comes with a full transcript. If you are offline, the transcript
still works.

### The screen

- **Left:** the steps of this scenario, with your progress.
- **Middle:** the lesson text for the current step.
- **Right:** the evidence: the **trace** (`USER → RAG → PLANNER → EXECUTOR → TOOLS →
  WORLD`), and the **Timeline**, **Forensics** and **Terminal** tabs.

### Run, then Check

Steps marked **RUN + CHECK** have two buttons, and the order matters:

1. **Run the attack**: performs the attack for real against the lab's tools. The
   timeline fills with what happened: the SQL that ran, the plan, the mail sent, and any
   `DEFENSE` line that stopped it.
2. **Read the timeline.** This is the lesson. The questions later in the scenario ask
   about what *your* run printed.
3. **Check the evidence**: reads what your run left behind and grades it. Check never
   runs anything itself, so a step cannot pass without a real run.

**Vulnerable or Secure?** The switch above the timeline sets the mode for one run.
Graded steps pick the right mode for you: the first run shows the attack landing
(*vulnerable*), a later step shows the same attack stopped (*secure*). You never need to
rebuild anything.

Steps marked **RECALL** are short questions. Answer from your own run, not from memory.
Steps marked **READ** just need reading.

**Next** opens only when the step's checks pass. *Skip this step* exists, but a skipped
step never counts toward the badge.

### Checking the evidence yourself

- **MailHog** (the lab's stand-in for an attacker's inbox): **http://127.0.0.1:8025**.
  In the exfiltration scenario, the stolen export really arrives here.
- **Forensics tab:** before and after for each data channel, and which file and function
  did the blocking.
- **Source links:** file names in the lessons (for example `tools/db_tool/server.py`)
  open the code on GitHub.
- **Terminal tab (optional):** a shell inside the lab network for the `curl` commands in
  the lessons. Start it with
  `docker compose -f docker-compose.yml -f docker-compose.terminal.yml up -d ttyd`.

---

## 5. Claim your badge

When all 9 Core scenarios are done:

1. Go back to the **AI & Agent Security** Area page and scroll to **Completion badge**.
   The meter reads *Core complete 9 / 9*.
2. Press **Claim badge**. Type the name you want on it (optional; it is not verified)
   and press **Issue badge**.
3. You get the badge emblem, a badge token, **Download badge (SVG)** and **Verify it**.
   Save the token: it is your badge.
4. **Verify it** opens the verify page, which shows *✓ Valid signature* and the
   transcript of all 23 checks with the mode each was graded in.

**What the badge proves, honestly:** every graded check passed on this lab instance,
after you ran the attacks yourself, and the transcript has not been edited since. It is
signed by your own instance, so it is tamper-evident, not a third-party certification.
Anyone verifying it should read the transcript, not just the title.

---

## 6. Something went wrong?

| What you see | What to do |
|---|---|
| The page at `127.0.0.1:8000` does not load | The lab is still starting. Wait a minute and refresh. Check `docker compose ps`: the `agent` service should be *Up*. |
| `port is already allocated` for 8000 | Another copy of the lab (or another app) uses port 8000. Stop it, or run `docker compose down` in the other lab folder. |
| The pre-flight panel says every tool **timed out** | The containers cannot reach each other. On Linux this is usually the host firewall (an iptables `FORWARD` policy of `DROP`). Fix it, then `docker compose up -d` again. |
| Start-up takes many minutes every time | The folder is probably synced (OneDrive, Dropbox). Clone into a normal folder. |
| **Check** says there is no run, or the wrong mode | Press **Run the attack** first, on this step. Check grades the run you just made, in the mode the step asks for. |
| A **RECALL** answer is marked wrong | Re-read your timeline. The answers come from what your run printed. |
| The video does not play | It streams from GitHub Pages and needs internet. Use the **Transcript** under the player. |
| **Claim badge** says checks are missing | It lists them. Open each one, Run and Check it again on this machine. Passes are recorded by the lab, not by your browser. |
| The live chat in the sandbox is slow or times out | That is the local AI model on a CPU. It is never needed for the graded path. |

Still stuck? Open an issue: https://github.com/uddeshya-world/agentic-security-lab/issues
with what you did, what you expected and what you saw (a screenshot helps).

---

## 7. Stopping, resuming and starting over

- **Stop:** `docker compose down` in the lab folder. Your progress is kept.
- **Resume:** `docker compose up -d`, then open http://127.0.0.1:8000/ again.
- **Start over from zero:** stop the lab, delete `data/ledger.json` (the lab's record
  of your passes), and clear this site's data in your browser (site settings for
  `127.0.0.1:8000`). Then start the lab again.

---

## 8. After the badge

- **Persistence** path: memory poisoning, MCP tool poisoning, a poisoned agent skill.
- **Operate** path: guardrails and observability in production, red-team evaluation,
  governance.
- **Reviewer** path: for officials and approvers; what to ask a vendor, no Docker needed.
- The **sandbox console** (`/lab/ui/index.html`) runs the whole attack catalogue against
  the live agent with no steps and no grading, for experimenting.

You should now be able to draw the agent's data path, name a control on every hop, and
say which control stopped which step and why. That is what the badge is about.
