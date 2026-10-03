# CyberRange — Product Flow

How a learner actually moves through this product, what they see, and what they walk away able to do.
Written from the running code, not from the pitch.

---

## 1. What this is

CyberRange is a self-hosted, guided security-lab platform. You run `docker compose up -d` on your own
machine and get a real, deliberately vulnerable **LLM agent stack** — a planner, an executor, a SQL
tool, an email tool, a file tool, a RAG store, a memory store, and a fake SMTP inbox — plus a browser
UI that walks you through exploiting it and then defending it. Every scenario follows one loop:
**attack it for real → build the control that stops it → measure the difference.** One Area is live
today: **AI & Agent Security**, 16 scenarios, 69 steps, 31 graded checks, ~255 minutes. Ten more
Areas (Web, Offensive, SOC, Cloud, DevSecOps, DFIR, Malware RE, Network, Crypto, GRC) are planned
and visible on the catalog as roadmap cards — they are copy, not product. Judge this as *one deep
course with a platform shell around it*, because that is what it is.

---

## 2. Who it is for

The Area declares its own audience in `content/areas/ai-security/area.json` — four `roles[]` and
three `certs[]`. The certs are frameworks, not proctored exams: **OWASP Top 10 for LLM Applications
(2025)**, **OWASP Agentic Security Initiative (2026)**, **MITRE ATLAS**. The only credential the
product issues is its own `ai-security-practitioner` badge, and that is browser-local (see §8).

| Persona | Chasing | What they can't do today |
|---|---|---|
| **AppSec engineer moving to AI** | AI Application Security Engineer; wants OWASP LLM Top 10 fluency | Finds SQLi in a web form in her sleep. Has never watched a *planner* emit `filter=1=1` on its own, and can't say whether the fix belongs in the model, the executor, or the tool. |
| **Pentester adding an LLM practice** | LLM / ML Red Teamer | Can jailbreak a chatbot. Has no repeatable way to demonstrate *impact* — a chain from poisoned document to data leaving the boundary — which is what a client pays for. |
| **Platform / infra engineer shipping agents** | AI Security Engineer | Owns an agent in production and has been asked "is it safe?" Has no vocabulary for the answer beyond "we prompt it not to." Needs the six control layers and where each one lives in code. |
| **Architect or GRC lead** | Security Architect (AI platforms) | Must map agent risk to OWASP LLM / ASI categories and show an auditor a decision trail. Has read the PDF; has never seen LLM01 or LLM06 actually happen. |

Prerequisites are honest: terminal + Docker Compose, enough Python to read a 15-line function, **no
ML background required**.

---

## 3. Why anyone would use it

| What exists | What it teaches | What it doesn't give you |
|---|---|---|
| Chatbot jailbreak playgrounds | Prompt tricks against a text box | No tools, no SQL, no email, no side effects. A tricked chatbot *says* something wrong; a tricked agent *does* something wrong — that gap is the whole field. |
| OWASP LLM Top 10 PDF | Names and definitions | You can recite LLM01 without ever having caused one. No target, no evidence, no before/after. |
| PortSwigger / DVWA | Excellent web-bug muscle memory | The app is a web app. Nothing about planners, retrieval as an input channel, or inter-agent trust. |
| Vendor "AI guardrail" demos | That the vendor blocks one hand-picked prompt | You don't own the code, can't see the failure mode, and get no catch-rate / false-positive / latency numbers. |
| University AI-security courses | Theory, papers, sometimes a notebook | Rarely a running agent you can break, and almost never the blue-team half. |

The wedge: **you exploit a working agent, then you can point at the line of code that should have
said no.** Nothing above lets you do both on the same system, and nothing above ends with a
measured before/after.

---

## 4. The end-to-end flow

**Start the stack.** `docker compose up -d` brings up `agent`, `ollama`, `ollama-init`, `db-tool`,
`email-tool`, `file-tool`, `mailhog`, `chroma`. Everything binds to `127.0.0.1` only. Ollama's
`11434` is deliberately **not** published — only the agent container reaches it. On boot the agent
ingests the benign corpus and warms the model in background threads so the first live attack is less
likely to time out.

**Catalog.** Open `http://127.0.0.1:8000/` → redirects to `/lab/ui/catalog.html`, which calls
`GET /catalog`. You see one **Available** card (AI & Agent Security: blurb, cert pills, role pills,
a `%` progress bar, and every scenario listed with minutes and check count) and ten greyed
**Roadmap** cards. The primary CTA is **Start AI Security**, which goes straight to orientation, not
to a blank console.

**Scenario page.** `/lab/ui/scenario.html?area=ai-security&id=00-orientation` loads
`GET /scenario/ai-security/00-orientation` and renders three columns:

- **Left rail** — the step list, each labelled `graded` or `read`, with a progress bar.
- **Centre** — the lesson. Markdown rendered by `marked`; the intro is prepended to step 1 and the
  finish block appended to the last step. Every code fence gets a **Copy** button, and any fence
  starting with `curl`, `docker`, `cat`, `python`, `pip` or `SECURE_MODE` also gets **To terminal**
  (which copies to clipboard and switches the right pane — it does not type into the shell).
- **Right** — **Run sim** bar (with a `container mode / force vulnerable / force secure` dropdown),
  then three tabs: **Timeline**, **Forensics** (planner plan / tool results / RAG context), and
  **Terminal**.

**Terminal.** An opt-in ttyd container at `127.0.0.1:7681`, started with
`docker compose -f docker-compose.yml -f docker-compose.terminal.yml up -d ttyd`. It mounts the repo
at `/app` and socat-forwards `127.0.0.1:8000/8101/8102/8103/8025` to the compose services, so every
lesson command runs **unmodified** — the same string a learner would type on their host. If it isn't
running, the pane shows the exact command to start it.

**A worked scenario — `01-tool-abuse-sqli`.**

1. *Step 1 — the vulnerable surface.* The lesson inlines the actual bug:
   `sql = f"SELECT * FROM {table} WHERE {filter_fragment}"`. No file-hunting required.
2. *Step 2 — fire it.* `curl -s -X POST http://127.0.0.1:8101/invoke -d '{"table":"customers","filter":"1=1"}'`.
   Then **Check** → `POST /scenario/ai-security/01-tool-abuse-sqli/check/step-02`. Verdict:
   *"PASS — SQL injection landed: filter=1=1 dumped multiple customer rows against the real database."*
3. *Step 3 — read the evidence.* The Timeline shows a real `SQL` line —
   `SELECT * FROM customers WHERE 1=1` — in a highlighted block, with the row count and
   `mode: vulnerable`. Against a real SQLite file, real synthetic rows.
4. *Step 4 — enable the defense.* Secure mode requires a bound `customer_id`;
   `queries.query_secure()` runs `SELECT ... WHERE customer_id = ?`.
5. *Step 5 — prove it.* Same payload, opposite outcome:
   `{"error": "customer_id required in secure mode", "defense": "SECURE_MODE rejects free-form SQL filter…"}`.
   Check verdict: *"Same payload, blocked."*
6. *Step 6 — optional, live.* `POST /run` with a natural-language prompt and watch qwen2.5:1.5b
   choose the injection itself. 30–120s on CPU, may time out, explicitly **ungraded**.

**Cross-tool exfil (`03`) is where impact lands.** The chain dumps customers then emails them to
`audit@external-logging.test` with subject `Customer Export Lab M01`. A `mailhog`-kind check queries
`http://mailhog:8025/api/v2/messages` and asserts the message is there — and you open
`http://127.0.0.1:8025` and read your own customer table in the body. That is the moment a finding
becomes an incident.

**The capstone (`04`) shows the guardrails naming themselves.** In secure mode the Timeline prints
`DEFENSE  SECURE_MODE: validating step via schema → least privilege → HITL → tool policy before
calling db_tool`, then `DEFENSE  GUARDRAIL blocked db_tool: … (SchemaValidationError)`, then an
`explain` line saying *which* layer fired, then `DEFENSE  Active: …` for each control. You do not get
"blocked" — you get *which control, at which hop*.

**Finishing.** The last step appends `finish.md` — "what you proved", the controls by id (C1, C2, …),
and a pointer to the next scenario. **Finish ✓** returns you to the catalog, where the completed
scenario shows a ✓ and the progress bar moves. When all 16 read as complete, the card's footer
swaps to **Claim certificate**, which opens a dialog: *AI Security Practitioner*, plus a 40-hex
"verification id."

---

## 5. The pedagogy

**Attack → defend → measure, on the same system, every time.** Most training picks a colour. Here
the contrast *is* the lesson: you cannot understand a control you have never seen stop something you
personally caused.

**Grading asserts lab state, not exit codes.** `lab/checks.py` supports four real check kinds:
`simulate` (run the attack in a forced mode, assert `success` / `blocked`, optionally require a named
guardrail event to have fired), `mailhog` (did the message actually reach the sink?), `lab_status`
(are the tool servers healthy?), and `secure_mode`. A generic terminal grader asks "did your script
exit 0?" This asks "did rows leave the database, did mail leave the boundary, did the guardrail
fire?" That's the technical differentiator, and it's why a learner can trust a green PASS.

**Deterministic sims alongside an optional live LLM.** A 1.5b model on CPU is slow and sometimes
doesn't take the bait. Grading a class on that is malpractice. So the graded path injects the exact
plan a prompt-injected model *would* emit and runs it through the **real executor** — the same choke
point production code uses — against **real tools**. Nothing is mocked except the model's decision.
The live model stays available (`POST /run`, `POST /lab/attack/{id}`) as the ungraded "yes, a real
LLM emits this" confirmation. Reliable teaching engine; honest bonus.

---

## 6. The 19-scenario curriculum

Values read verbatim from each `scenario.json`. Total: **308 minutes, 81 steps, 43 graded checks.**

| # | Scenario | You attack | You build | OWASP / ASI (as declared) | Controls | Min |
|---|---|---|---|---|---|---|
| 0 | What is an agent with tools? | nothing — you map the data path and find the trust boundary | — | — | — | 8 |
| 1 | Tool abuse — SQL injection (no LLM needed) | `db_tool`'s free-form `filter` → `WHERE 1=1` | parameterized/scoped query + schema allow-list | LLM03:2026 Excessive Agency · ASI02 Tool Misuse | C1 C2 C3 C7 | 15 |
| 2 | Poison the LLM context (RAG) | plant a poisoned shipping FAQ; benign question retrieves it | RAG trust/provenance filter | LLM01:2026 Prompt Injection · LLM05:2026 Data and Model Poisoning · LLM09:2026 Vector and Embedding Weaknesses · ASI06 Memory and Context Poisoning | C6 C7 | 15 |
| 3 | Cross-tool exfiltration (dump → email) | chain `db_tool` → `email_tool` to an external address | egress allow-list + human-in-the-loop gate | LLM02:2026 Sensitive Information Disclosure · LLM03:2026 Excessive Agency · ASI02 Tool Misuse | C1 C4 C5 C7 | 18 |
| 4 | Exploit the agent (RAG → planner → tools) | full kill chain through the real executor | all six layers at once; re-inject the plan | LLM01:2026 Prompt Injection · LLM03:2026 Excessive Agency · ASI01 Agent Goal Hijack · ASI02 Tool Misuse | C1 C2 C4 C5 C6 C7 | 25 |
| 5 | Guardrail map — what to build and where | no attack — you design from memory | the six-layer control map | LLM01:2026 Prompt Injection · LLM02:2026 Sensitive Information Disclosure · LLM03:2026 Excessive Agency · ASI02 Tool Misuse · ASI03 Identity and Privilege Abuse | C1 C2 C3 C4 C5 C6 C7 C21 | 15 |
| 6 | Deep RAG poisoning — crowding & false provenance | flood top-k with near-duplicates; mislabel poison as `trust=seed` | content-aware poison detector | LLM01:2026 Prompt Injection · LLM05:2026 Data and Model Poisoning · LLM09:2026 Vector and Embedding Weaknesses · ASI06 Memory and Context Poisoning | C6 C8 | 20 |
| 7 | Multi-agent attacks — tampering & rogue agents | rewrite an unsigned plan in transit; smuggle an unregistered tool | HMAC-signed messages + agent/tool allow-list | ASI07 Insecure Inter-Agent Communication · ASI01 Agent Goal Hijack · ASI10 Rogue Agents | C9 C10 | 18 |
| 8 | Memory poisoning — the persistent backdoor | write an instruction into long-term memory; recall it in a fresh session | memory write validation + provenance signing | ASI06 Memory and Context Poisoning · LLM01:2026 Prompt Injection · ASI01 Agent Goal Hijack | C11 C12 | 18 |
| 9 | Production guardrails & observability | run a labeled probe set with scanners off | measured input/output pipeline: catch rate, FP rate, p50/p95 | LLM01:2026 Prompt Injection · LLM02:2026 Sensitive Information Disclosure · LLM10:2026 Improper Output Handling | C13 | 16 |
| 10 | Red-team evaluation pipeline | every module's attack as one battery | attack-success-rate suite wired into CI | LLM01:2026 Prompt Injection · LLM02:2026 Sensitive Information Disclosure · LLM03:2026 Excessive Agency | C14 | 15 |
| 11 | Supply chain — rogue tools & MCP servers | register an unmanifested tool; tamper a manifest to escalate | signed capability manifests + startup attestation | LLM04:2026 Supply Chain · ASI04 Agentic Supply Chain · ASI10 Rogue Agents | C15 | 16 |
| 12 | Governance & policy-as-code | the always-allow policy stub | blast-radius decision matrix + queryable audit trail | LLM03:2026 Excessive Agency · ASI03 Identity and Privilege Abuse | C16 C17 | 16 |
| 13 | System prompt leakage | make the planner recite tool names, arg shapes, the dump-all example | outbound leak detection (and why the real fix is upstream) | LLM08:2026 Hidden Context Exposure · LLM01:2026 Prompt Injection | C18 | 14 |
| 14 | Misinformation — groundedness & citations | a confident refund policy supported by no source | groundedness/citation enforcement | LLM07:2026 Misinformation · LLM05:2026 Data and Model Poisoning | C19 | 15 |
| 15 | Unbounded consumption — denial of wallet | one valid tool call, repeated 40 times | step cap + cost budget + loop detection + rate limit | LLM06:2026 Unbounded Consumption | C20 | 14 |
| 16 | Direct prompt injection & jailbreak | a chat message — not a poisoned document — steers the planner into the same dump | executor-side policy: the plan is a proposal, never an authorization | — | LLM01:2026 Prompt Injection · LLM03:2026 Excessive Agency | C2 C7 | 15 |
| 17 | Data guards — DLP for agents | email the customer table past a domain allow-list | four-channel DLP: classify, then mask or block on prompt, RAG, output, tool results | — | LLM02:2026 Sensitive Information Disclosure · LLM10:2026 Improper Output Handling · ASI03 Identity and Privilege Abuse | C21 C4 C13 | 20 |
| 18 | Agent identity & confused deputy | a hijacked plan spends the tool's broad credential on everyone's rows | bind `customer_id` from the session, not from the model | — | ASI03 Identity and Privilege Abuse · LLM03:2026 Excessive Agency | C1 C7 | 15 |

`lab/curriculum.py` also publishes the honest denominator: all ten LLM Top 10 categories covered,
and the ASI list is the full official ASI01–ASI10 with the **uncovered** entries left in — ASI05
(unexpected code execution), ASI08 (cascading failures) and ASI09 (human-agent trust exploitation)
are marked `covered: False`. The coverage number isn't self-selected.

---

## 7. What it proves about the learner

**Interview answers you can now give:**

- *"Where does the control go?"* — draw `user → RAG → planner → executor → tools → world` and name a
  control on every hop. That is scenario 5, and it is the answer most candidates cannot give.
- *"Is the model the vulnerability?"* — no; scenario 1 lands with the LLM entirely out of the loop.
  The tool is the bug; a steered planner is one caller among many.
- *"How do you prove a guardrail works?"* — same payload, two modes, an assertion against real state,
  and an attack-success rate you can put a number on (scenario 10).
- *"Why isn't a trust label enough?"* — because it's attacker-supplied (scenario 6).

**Portfolio artifacts:** a before/after attack-success table, a MailHog message that is your own
exfiltrated data, DEFENSE timeline output naming each layer, a guardrail effectiveness dashboard
(catch rate / FP / latency), and a red-team CI workflow that fails the build on regression.

---

## 8. Honest limitations right now

Twelve items were listed here when this document was written. Seven have since been
fixed and are recorded below as fixed, because a limitations section that quietly
drops its entries is not a limitations section. The rest still stand.

### Fixed

| Was | Now |
|---|---|
| Check ran the attack *and* graded it, so every scenario was completable without typing a command | `evidence` checks grade the run the learner performed, recorded in `lab/runlog.py`. No run, no pass — and a run made for one step does not grade another |
| Opening a read-only step marked it complete, so orientation could be Next-spammed to 100% | Read steps require an explicit "Mark read", and three of them now carry server-graded `recall` questions whose answer key never ships to the browser |
| The certificate was `SHA-256(area\|credential\|count\|Date.now())` — a hash of the current time | `lab/credential.py` issues an HMAC-signed, Open Badges-shaped assertion carrying the full transcript of graded passes, gated on every graded check. `/lab/ui/verify.html` checks the signature and shows the transcript |
| "SECURE_MODE" named three mechanisms, and the lesson text referenced a fourth button that did not exist | One per-run mode switch in the stepper. The phantom sentence is gone from `01/step-04.md` and `02/step-04.md`, and `/lab/status` returns a structured `secure_mode_help` separating per-run from persistent |
| `@media (max-width:1040px) { .rightcol { display: none } }` hid the evidence — the point of the lab | No rule hides the evidence column at any width. Below 1180px it stacks under the lesson and the Check button. Verified at 1440 / 1180 / 1024 / 820 / 390 |
| Roadmap cards looked clickable, and the catalog counted eleven areas as if they were product | The roadmap is a non-interactive index. Counts are derived: "1 live · 11 planned", with Areas being authored shown as *in progress* rather than as either |
| Two brands and no way back: the catalog said *CyberRange*, the console said *Agentic Security Lab* | One brand, **CyberRange**. The console is the *sandbox console*, reachable from the catalog and with a link back to it |

### Still true

1. **Content is parsed once per process.** `lab/content.py` caches the tree with
   `@lru_cache(maxsize=1)`, so a long-running instance serves a stale catalog after
   new scenarios land on disk. `POST /lab/content/reload` fixes it; nothing calls it
   automatically.
2. **No next-scenario handoff.** `finish.md` says "Next: *RAG poisoning*" as prose,
   but the Finish button navigates to the catalog. The sequence exists in the
   writing, not in the UI.
3. **Live-LLM UX is rough.** No progress state for a 30–120s run, and a successful
   exploit can end with an empty `final_answer` — the planner dumps the table, then
   calls `answer` with `{}` — which reads as failure.
4. **The mail sink has no per-run tag.** Identical `Customer Export Lab M01` messages
   accumulate, so the proof is a pile of twins and "nothing new arrived" is not a
   claim the sink can support. The Blue Team area now teaches this as a real
   evidence problem rather than hiding it, but the sink is still untagged.
5. **Files you are asked to open have no viewer.** Scenario 1 inlines its bug;
   orientation still says "open `agents/executor.py`" with no in-page reader unless
   the terminal panel is up.
6. **The badge is signed by the instance that issues it.** That makes it
   tamper-evident, not third-party attested. Whoever runs the lab holds the key. The
   badge and the verify page both say so; real attestation needs a hosted issuer.
7. **Progress is per-browser.** `localStorage` under `cr:progress:<area>:<scenario>`.
   Clear site data and the transcript is gone. Server-side progress is the
   prerequisite for the badge meaning anything to a third party.

---

## 9. Where it goes next

Staged, in dependency order. Nothing here is a new Area until the existing one is airtight.

**Stage 1 — content and doc truth (days).** Delete the phantom "Enable SECURE_MODE" sentence from
`01/step-04.md` and `02/step-04.md`; reconcile README / ROADMAP / LEARN with what actually ships;
call `content.reload()` on a file-watch or drop the `lru_cache`; inline the executor trust boundary
the way scenario 1 inlines its SQL; tag MailHog subjects per run.

**Stage 2 — interaction model (weeks).** Split **Run** (executes, fills the Timeline) from **Check**
(asserts evidence only) so the green PASS follows looking at the SQL. Add two or three recall prompts
per scenario ("paste the SQL that ran", "name four places a control can sit") so read-steps stop
auto-completing. Collapse SECURE_MODE into one visible toggle — *this graded run: vulnerable |
secure* — with a note that recreating containers is the optional persistent path. Stack the evidence
column under the lesson instead of hiding it below 1040px. Give the console one brand, one back-link,
and a role as the free-fire sandbox linked from later steps.

**Stage 3 — server-side progress (weeks).** Move progress out of `localStorage` and behind an
identity, enable **Claim** only when the graded steps actually passed, and make the credential
verifiable. Until then, label it a browser badge.

**Stage 4 — additional Areas (months).** The engine is already environment-agnostic — `area.json`
declares its own `env`, and checks are declarative JSON. Web AppSec is the natural second Area
because the check vocabulary (assert real state) transfers directly. Ship one, not ten.

**Stage 5 — distribution.** Publish the flagship Area in an existing platform's scenario format as a
funnel rather than fighting for cold traffic, and lead with the sentence that actually sells it:
*"I exploited an agent, then I pointed at the line of code that should have said no."*
