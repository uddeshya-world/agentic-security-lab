# CyberRange — End-to-End Plan

> **Status:** execution plan (2026-09-03). Companion docs: [PRODUCT_FLOW.md](PRODUCT_FLOW.md) (what a learner does today), [CURRICULUM.md](CURRICULUM.md) (full Area map).
>
> **Decision already taken:** start with **one live course** (AI & Agent Security). Stand up the next main courses **in parallel**, as thin slices, without waiting for AI to be “finished” and without pretending ten roadmap tiles are product.

**Goal:** turn the running AI lab into a real multi-course security range — Killercoda lab grammar, DVWA-for-agents depth — while a stranger can still finish a useful path on day one.

**Architecture:** one **lesson engine** (catalog → stepper → checks → credential). Each **course (Area)** brings its own environment overlay and content tree. Courses ship independently. The catalog only marks an Area `available` when it meets the live bar below.

---

## 0. How to read this

| If you want… | Read |
|---|---|
| What to do this week | §12 Immediate next actions |
| Why not 10 courses at once | §2 Strategy |
| What “live” means | §3 Live bar |
| How parallel work actually runs | §5 Parallel operating model |
| AI remaining work | §6 Course 1 |
| Fastest second course | §7 Course 2 (Blue Team, same stack) |
| First *new* stack | §8 Course 3 (Web AppSec) |
| Platform work that unblocks everyone | §4 Kernel |
| Later Areas | §9 |
| Business / hosted / Killercoda | §10 |

This plan assumes a small team (you + coding agents). It is sequenced so **one person can execute Course 1 + kernel**, and extra hands/agents attach to Course 2/3 without blocking.

---

## 1. What CyberRange is (and is not)

**Is:** a self-hosted, browser-guided security lab. Pedagogy is fixed:

```text
exploit it for real → build the control → measure the delta
```

Check asserts **lab state** (rows dumped, mail landed, guardrail fired, flag captured) — not `verify.sh` exit 0. That is the difference vs Killercoda. The difference vs TryHackMe/HTB is the **same system is red and blue**, plus a before/after number.

**Is not (yet):** a hosted Kubernetes playground, an OSCP replacement, or a marketplace of community labs. Catalog roadmap cards for Web/OSCP/Cloud are **intent**, not inventory. Do not market 11 Areas.

**Brand (lock this):**

| Surface | Name |
|---|---|
| Product | **CyberRange** |
| Flagship Area | **AI & Agent Security** |
| Repo / stack | agentic-security-lab (fine to keep as the engine name) |
| Credential issuer | CyberRange (self-hosted) — done: `lab/credential.py` issues as `CyberRange (self-hosted instance)` |

One name in the catalog, the console, Swagger, and the badge.

---

## 2. Strategy: one live, then parallel slices

Killercoda won by being a **platform** with many shallow labs. We cannot out-catalog them. We win by being the place you **break an agent (then a web app, then hunt the traces)** with evidence.

### 2.1 The wedge

1. **Own AI/agent security** — no dominant hands-on curriculum exists.
2. **Own attack→defend→measure** as a format other platforms treat as two products.
3. **Use other Areas to become a destination**, not to look big.

### 2.2 Why “start with one”

AI is already running: real SQL, real SMTP, real RAG, 16 scenarios on disk, hosted demo compose, lesson engine. Shipping a half-baked Web Area next to it would make the flagship look like vapor too.

**Rule:** only one new Area may flip `status: available` per release train. Others may be `authoring` (visible to maintainers, hidden or clearly “coming” on the catalog).

### 2.3 Why parallel anyway

Waiting until AI is perfect means Web never starts. Content authoring, env builds, and platform kernel are **independent** once the contracts in §4 exist.

The trick: **do not parallelize 10 full curricula.** Parallelize **three workstreams** that share the kernel:

```text
                    ┌─ A. AI Security     (LIVE now — polish, don’t rebuild)
Kernel (engine) ────┼─ B. Blue / SOC      (SAME docker stack — fastest 2nd course)
                    └─ C. Web AppSec      (NEW compose overlay — first new env)
```

Everything else (Offensive, Cloud, DFIR, Malware, Network, Crypto, GRC, DevSecOps) stays **spec-only** until B or C has met the live bar. That is the anti-sprawl rule.

### 2.4 What “main courses live in parallel” means in practice

Learners will see, in order of appearance:

| When | Catalog “Available” | What they run |
|---|---|---|
| **Now** | AI & Agent Security | `docker compose up -d` |
| **Train 1** (same stack) | AI + Blue Team | same compose; Blue reads MailHog, events, logs |
| **Train 2** (new stack) | AI + Blue + Web | `compose.yml` + `docker-compose.web.yml` |
| Later | add one Area per train | its own overlay |

Three live courses. Two stacks. That is enough to look like a range without becoming a fake Killercoda.

---

## 3. Live bar — an Area is not live until all of this is true

Copy this into PR review. If any box is open, the Area stays `authoring`.

**Environment**

- [ ] `area.json` has `status`, `env.compose`, `env.services`, `env.requires`
- [ ] `docker compose -f <that file> up -d` brings a healthy target on `127.0.0.1` only
- [ ] Hosted overlay (`LAB_HOSTED=1`) serves catalog + lessons **without** attack routes or tool servers
- [ ] A one-command smoke: `GET /lab/status` (or Area equivalent) shows the env healthy

**Curriculum**

- [ ] Orientation (no attack) + **at least two** graded exploit→defend scenarios + one “map / what you built”
- [ ] Every graded step has a check that asserts **state**, not “sim ran”
- [ ] Vulnerable and secure (or patched) paths exist; student sees before/after
- [ ] 30–45 minute “first win” path documented (`docs/LEARN-<area>.md` or a catalog CTA)

**Product**

- [ ] Catalog tile: blurb, certs, roles, scenario list, progress
- [ ] Stepper works at 1280px **with Timeline visible** (do not `display:none` the evidence column)
- [ ] Credential uses the signed transcript (`lab/credential.py`), not a timestamp hash
- [ ] Tests: content loads, every check `kind` is registered, at least one env integration test

**Honesty**

- [ ] Roadmap cards are labelled coming / authoring — not clickable as labs
- [ ] Search count is “N live Areas”, not “11 areas”

Thin-slice size for a **new** Area: **4 scenarios, ~60–90 minutes**, not 16. Grow after live.

---

## 4. Platform kernel — what must be Area-agnostic

Today the **content loader** is Area-agnostic (`content/areas/<id>/`). The **runtime** is not: one `docker-compose.yml`, AI tools, `lab/simulate.py`, MailHog checks, a hardcoded ROADMAP array in `catalog.html`.

Kernel work unblocks every parallel course. Do this once.

### 4.1 Contracts (freeze these)

```text
content/areas/<area-id>/
  area.json                 # id, title, status, env, certs, roles, credential
  exploits/*.json           # optional (console prompts)
  scenarios/<slug>/
    scenario.json
    intro.md | finish.md | step-NN.md
    checks/step-NN.json     # { kind, ... }

env/<area-id>/
  docker-compose.yml        # OR repo-root docker-compose.<area>.yml
  README.md                 # how to start, ports, safety
```

`area.json.env.compose` must be **used**, not decorative. Catalog “Start” tells the student which compose file. A later `scripts/up.ps1 -Area web` reads that field.

### 4.2 Check kinds (plugin list)

Keep existing AI kinds. Add generic ones **before** Web is authored so writers don’t invent one-off graders.

| Kind | Meaning | Used by |
|---|---|---|
| `lab_status` | services healthy | all |
| `evidence` | last Run’s result / events | AI (preferred) |
| `simulate` | lab runs a deterministic attack (legacy AI) | AI |
| `mailhog` | message in sink | AI, Blue |
| `recall` | server-side multiple choice | all (stop Next-spam) |
| `http` **new** | GET/POST URL, assert status/body | Web |
| `file_contains` **new** | file on lab volume matches | Web, DFIR later |
| `flag` **new** | captured flag equals | Offensive later |
| `secure_mode` | persistent mode | AI |
| `manual` | acknowledgement only | rare |

Rule: **Run does the work. Check reads state.** `simulate` that auto-fires the attack is allowed only for orientation/health. Graded exploit steps must fail if the student never Ran.

### 4.3 Compose model

```text
docker-compose.yml                 # engine: agent UI + lesson API (always)
docker-compose.ai.yml              # today’s tools/ollama/mailhog  (alias of current file is fine)
docker-compose.web.yml             # NEW: vulnerable app + db
docker-compose.terminal.yml        # already exists
docker-compose.hosted.yml          # already exists — catalog only
```

Short term (start with one): **keep current `docker-compose.yml` as the AI stack.** Do not reshuffle files until Web’s overlay exists. When Web lands, split:

- `docker-compose.yml` = UI/engine only (or AI remains default because it is the flagship)
- `docker-compose.web.yml` = Web target
- Catalog Start button: `compose up` for the Area’s `env.compose`

Safety invariant (never drop): attack stacks bind `127.0.0.1`. Hosted compose ships **no** tool servers.

### 4.4 Catalog

- Load Areas from `GET /catalog` only.
- `status: available | authoring | roadmap`.
- Stop counting hardcoded ROADMAP toward “11 areas”.
- CTA: **Start &lt;Area&gt;** → first scenario. Secondary: classic console **only for AI**.

### 4.5 Progress and credentials

- Progress today is `localStorage`. Acceptable for v1; Course 2 should still work that way.
- Issue badge via `lab/credential.py` (HMAC transcript). Issuer name unified to CyberRange.
- Phase “accounts” is **after** three live Areas, not before. Don’t build login to look like a startup.

### 4.6 Kernel tasks (do in Train 0, ~1 week, unblocks B and C)

1. Catalog: live count vs roadmap; hide empty Areas from search-as-product.
2. Register check kinds in one table; tests list them (`tests/test_content_engine.py` is already the gate).
3. Document the Area folder template: `content/areas/_template/`.
4. `area.json.env` rendered in the catalog tile (“needs Docker; compose file X”).
5. Brand pass: CyberRange everywhere the student looks (catalog, console header, `/docs` title, credential issuer).
6. Scenario layout: Timeline stays visible ≥1100px; stack under the lesson on smaller screens — **never hide evidence**.

None of this requires a second course. It makes the second course cheap.

---

## 5. Parallel operating model

### 5.1 Workstreams (can run in the same week)

| Stream | Owner (you or an agent) | Depends on | Does not wait for |
|---|---|---|---|
| **K — Kernel** | platform | nothing | content polish |
| **A — AI live** | content + small UX | running stack (done) | Web |
| **B — Blue Team** | content | AI events/MailHog (done) | Web env |
| **C — Web** | env + content | kernel check kinds `http` | AI modules 13–15 |

A, B, C never edit each other’s `content/areas/<id>/` trees. Kernel PRs don’t mix scenario prose.

### 5.2 How to actually parallelize with agents

Give each agent a **closed Area folder** and the live-bar checklist. Do not give three agents the same `catalog.html`.

```text
Agent K:  lab/checks.py + lab/ui/catalog.html + tests/test_content_engine.py
Agent A:  content/areas/ai-security/**  (polish only)
Agent B:  content/areas/blue-team/**    (new tree) + checks that only read MailHog/events
Agent C:  env/web/** + content/areas/web-appsec/** + a tiny vulnerable app
```

Merge order: **K first** if it changes check schemas; otherwise A/B/C can merge independently.

### 5.3 Release train (every 2 weeks)

1. Kernel + any Area that meets the live bar.
2. At most **one** new `available` Area.
3. Demo: 15-minute recording of the new first-win path.
4. Update `docs/LEARN.md` / Area LEARN page.

If nothing meets the bar, ship AI polish only. Empty trains are allowed. Fake Areas are not.

### 5.4 Content factory (one scenario, any Area)

Do not invent a new format. Copy AI:

1. Write `scenario.json` (title, order, difficulty, minutes, owasp/controls).
2. `intro.md` — threat in one screen.
3. Steps: map → exploit (graded) → read evidence → enable control → prove blocked (graded) → optional live/manual.
4. Checks: vulnerable expect `success`, secure expect `blocked` / absence of mail / HTTP 403.
5. `finish.md` — what you can say in an interview.
6. One test: payload loads; graded checks have known `kind`.

Author **markdown before the env is pretty**, but do not mark the Area available until checks pass against the real target.

---

## 6. Course 1 — AI & Agent Security (LIVE — start here)

This is the only course students should be sent to **this week**.

### 6.1 Already true

- Stack: agent, ollama, db/email/file tools, MailHog, Chroma.
- Catalog + stepper + classic console + hosted compose.
- Scenarios 00–15 on disk; 00–12 served if the agent process has current content (reload/restart after adding 13–15).
- Deterministic sims + optional live LLM.
- Real evidence: SQL dump, MailHog body, DEFENSE lines.

### 6.2 Remaining to call Course 1 “flagship-quality” (not a blocker for B/C)

Priority order:

| P | Item | Why |
|---|---|---|
| P0 | Content reload / restart so 13–15 appear in `/catalog` | Students can’t find authored lessons |
| P0 | Run vs Check: graded steps fail without a prior Run (`evidence` kind) | Otherwise Check is a skip button |
| P0 | Timeline visible on laptop widths | Evidence is the product |
| P1 | SECURE_MODE: one UI control; delete “Enable SECURE_MODE” copy that points at a missing button | Student confusion |
| P1 | Live-agent empty `answer` → banner that SQL still ran | Looks like failure today |
| P1 | Brand: CyberRange on console + Swagger | Two-product feeling |
| P1 | Credential issuer name + don’t claim LinkedIn-grade cert | Honesty |
| P2 | `{{exec}}`-style send-to-ttyd (optional) | Killercoda parity, not wedge |
| P2 | MailHog subjects tagged with run id | Duplicate inbox noise |
| P2 | `docs/LEARN.md` matches `/` → catalog | Stale docs |

### 6.3 AI first-win path (keep this as the homepage CTA)

1. Orientation (map the agent).
2. SQLi on `db_tool` (no LLM).
3. RAG poison.
4. Exfil + MailHog.
5. Full agent exploit.
6. Guardrail map.

That is **Module 1 (00–05)**. Modules 2–8 stay in the same Area as advanced. Do not split them into a second catalog tile.

### 6.4 Do not do for AI right now

- Multi-tenant SaaS.
- Real NeMo/Garak production backends (seams are enough until Blue Team needs telemetry).
- Publishing to Killercoda **before** the local first-win is airtight (then use Killercoda as a funnel, per CURRICULUM.md).

---

## 7. Course 2 — Blue Team / SOC (parallel, **same stack**)

This is the fastest second **main course**. It does not need a new vulnerable app.

### 7.1 Why this is the parallel trick

The AI stack already produces:

- Execution timeline / events
- Real SMTP in MailHog
- SQL strings
- OTel seams
- Attack-success metrics

A SOC course is: **here is the incident the red team just caused; detect it, write the rule, prove it fires.**

That is unique. TryHackMe SOC labs are generic. Ours are **the same agent breach**.

### 7.2 Thin slice (live bar = 4 scenarios)

| # | Scenario | Student does | Check |
|---|---|---|---|
| 0 | Where agent telemetry lives | Map events, MailHog, status JSON | `lab_status` + `recall` |
| 1 | Catch the exfil | After (or including) a dump→email, find the MailHog message and name IOC (recipient, subject, body shape) | `mailhog` + `recall` |
| 2 | Write a detection | Given a timeline dump, identify the DEFENSE-absent pattern; author a simple rule (JSON/Sigma-lite in repo) | `file_contains` or structured `evidence` |
| 3 | Measure | Vulnerable run: alert must fire. Secure run: attack blocked, alert should *not* claim success | `evidence` / simulate in both modes |

Env: **current compose**. Maybe add OpenSearch later; **do not block live on a SIEM**. MailHog + `/lab/events` is enough for v1.

### 7.3 Folder

```text
content/areas/blue-team/
  area.json          # status: authoring until live bar
  scenarios/00-orientation/
  scenarios/01-catch-the-exfil/
  scenarios/02-write-the-detection/
  scenarios/03-before-after-alert/
```

`env.compose`: `docker-compose.yml` (same as AI). `env.notes`: “Start the AI stack; this Area consumes its telemetry.”

Catalog: show as Available only when the four scenarios grade green. Until then, a single line on the AI card: “Blue Team (authoring) — hunt the same incident.”

### 7.4 Parallelism with Course 1

Blue content can be written **this week** while AI polish happens. Checks only read MailHog/events. No new Docker services. This is the definition of parallel without extra infra.

---

## 8. Course 3 — Web Application Security (parallel, **new stack**)

Highest demand, clearest cert path (PortSwigger / eWPT). First time the kernel must support a second compose.

### 8.1 Thin slice (do not clone DVWA’s whole catalog)

| # | Scenario | Target | Defend |
|---|---|---|---|
| 0 | Orientation | App map, proxy optional | — |
| 1 | SQLi | login/search concatenates input | parameterized query; same payload blocked |
| 2 | Broken access / IDOR | `/orders/1` → `/orders/2` | authz on object id |
| 3 | SSRF or stored XSS (pick one) | one real impact | one control |
| 4 | Map | OWASP Web Top 10 vs what you touched | `recall` |

Skip a 10-vuln junkyard. Four labs, same loop as AI. Students who finish should be able to say “I exploited it, I patched this function, I retested.”

### 8.2 Environment

A **tiny** Flask/FastAPI app in `env/web/` (or `apps/web-target/`):

- Intentionally vulnerable routes behind `SECURE_MODE` (same teaching flag — students already know it).
- SQLite with synthetic users/orders.
- Bind `127.0.0.1:9000` (don’t collide with 8000/8101).
- Engine (CyberRange UI on :8000) talks to it for checks (`http` kind).

```text
docker-compose.web.yml
  web-target   # vulnerable app
  web-db       # optional; can be a file volume
```

Learner:

```text
docker compose -f docker-compose.yml -f docker-compose.web.yml up -d
```

Or, once `scripts/up.ps1 -Area web` exists, that.

**Do not** require Burp in v1. Browser + curl in ttyd is enough. Mention Burp as optional.

### 8.3 Parallelism with A/B

| Week | Agent C (Web) | Agent B (Blue) | Agent A (AI) |
|---|---|---|---|
| 1 | Vulnerable app + SQLi route + compose overlay | Area folder + scenario 0–1 markdown | P0 polish |
| 2 | IDOR + secure branches + `http` checks | Scenario 2–3 + MailHog checks | P1 UX |
| 3 | XSS/SSRF + LEARN-web.md + live bar review | Flip `available` if bar met | Content reload 13–15 |

Web **cannot** go available in week 1. Blue **can**. That is expected.

### 8.4 What we refuse for Web v1

- Full PortSwigger clone.
- A separate hosted attackable web app on the public internet.
- Teaching JWT/OAuth before SQLi+IDOR work.

---

## 9. Later courses (do not start env work)

Keep [CURRICULUM.md](CURRICULUM.md) as the long map. Execution order after three lives:

| Next | Why then | Env cost |
|---|---|---|
| 4. Network & Fundamentals | On-ramp for people who bounced off AI | pcaps + maybe compose hosts |
| 5. Cloud | LocalStack; after Web patterns exist | medium |
| 6. DevSecOps | CI on the Web app’s repo | medium |
| 7. Offensive | Needs a box image; isolation story | high |
| 8. DFIR | Images; no egress | high |
| 9. GRC | Reuse AI policy engine | low, but niche |
| 10. Malware RE | Safety-critical isolation | highest — last |
| 11. Crypto | Small services | medium |

**Hard rule:** no compose file, no `status: available`, until the previous live Area has a first-win path a stranger completed without you in the room.

GRC can piggyback AI module 12 (policy-as-code) as a **scenario track**, not a new Area, if you want a cheap extra tile. Prefer not to — it dilutes the catalog.

---

## 10. Delivery, hosted, and money

### 10.1 Three surfaces (already designed — keep)

| Surface | Compose | What it is |
|---|---|---|
| **Local lab** | `docker-compose.yml` (+ Area overlays) | Real attacks. Default. |
| **Hosted demo** | `docker-compose.hosted.yml` | Catalog + read-only lessons. No tools, no `/run`. |
| **Killercoda funnel** | later export of 1–2 AI scenarios | Traffic, not source of truth |

Do not run the vulnerable agent on a public IP. Hosted is a brochure that tells you to clone.

### 10.2 Monetization (after 3 live Areas, not now)

1. Free: local lab + hosted catalog + completion transcript.
2. Paid later: accounts, saved progress, proctored “AI Security Practitioner”, maybe instructor packs.
3. Do not put a paywall in front of SQLi-on-an-agent. The wedge has to be felt.

### 10.3 Distribution

- README + LEARN path + one 8-minute demo video (SQLi → MailHog → SECURE_MODE).
- Writeups: each `FINDINGS-*.md` / `finish.md` is a blog post.
- Killercoda: port **orientation + SQLi only** as a teaser that says “full agent is local.”

---

## 11. Phased timeline

Assumes part-time you + 1–2 coding agents. Calendar time, not fantasy sprint-team time.

### Train 0 — now → 2 weeks — “one course, real product”

**Goal:** a stranger finishes AI 00–05 and believes the product.

- Kernel: catalog honesty, brand, Timeline visibility, check-kind registry, Area template.
- AI: P0 items in §6.2.
- Blue: folder + scenario 0–1 drafted (not live).
- Web: env spike (hello-world vulnerable app on :9000) behind a branch, not catalog.

**Exit:** AI first-win is clean. Catalog does not lie about 11 Areas.

### Train 1 — weeks 3–4 — “two courses, one stack”

- Blue Team meets live bar (4 scenarios).
- Flip `blue-team` to `available`.
- AI P1 polish continues in parallel.
- Web: SQLi + IDOR working in compose overlay; still `authoring`.

**Exit:** student can attack the agent, then hunt the same exfil as a SOC.

### Train 2 — weeks 5–8 — “three courses, two stacks”

- Web thin slice meets live bar.
- `scripts/up.ps1 -Area web` (or documented compose files).
- Hosted demo lists three Areas, attack routes still stripped.
- LEARN pages: AI, Blue, Web.

**Exit:** CyberRange looks like a range. Still no OSCP tile.

### Train 3 — after that

- Accounts only if hosted demand is real.
- Network on-ramp **or** deepen Web (XSS, auth) — pick based on who showed up.
- Killercoda teaser export.

---

## 12. Immediate next actions (start with one)

Do these in order. Stop after step 6 if you have no extra agent this week.

1. **Keep AI as the only Available Area** in the catalog students see.
2. **Restart/reload agent** so scenarios 13–15 appear if they are meant to be live; if they are not ready, don’t advertise 16.
3. **Fix the first-win UX** (Timeline visible, Run vs Check, SECURE_MODE copy, brand).
4. **Add `content/areas/_template/`** so Blue/Web authors don’t invent structure.
5. **Open `content/areas/blue-team/`** as `authoring` — four scenario stubs, no catalog CTA.
6. **Spike `env/web`** in a branch: one SQLi endpoint, `SECURE_MODE` branch, port 9000.
7. Only then: register `http` check kind + tests.

That is “start with one” and “parallel main courses” without splitting the brain.

---

## 13. Risks

| Risk | Mitigation |
|---|---|
| Catalog looks like 11 products | Train 0 honesty; `authoring` ≠ `available` |
| Check button does the lab | `evidence` kind; fail if no run |
| Web becomes a second unfinished AI | Thin slice of 4; live bar is a gate |
| Docker complexity explodes | Default compose remains AI; overlays opt-in |
| Public hosted demo becomes an open proxy | Hosted compose has no tools; never publish 8101 |
| Parallel agents conflict | One Area tree per agent; kernel PRs separate |
| Certificate overclaim | Transcript + “self-hosted, not proctored” on the badge |
| Trying to beat Killercoda at K8s | Don’t. Refer CKA people to them. |

---

## 14. Success metrics (honest)

**Course 1 (now)**

- Stranger completes 00–05 in &lt; 90 minutes without a Slack thread.
- SQLi Check fails if they didn’t run; passes with real `WHERE 1=1`.
- MailHog shows the customer dump after exfil.

**Course 2**

- After an AI exfil, Blue scenario 1 Check passes on the **same** MailHog message.
- Student can name one IOC and one control that would have stopped it.

**Course 3**

- `compose` overlay up; SQLi + IDOR each have vulnerable PASS and patched PASS.
- No AI services required for those two Web labs.

**Product**

- Catalog “N areas” = number of `available` Areas.
- Hosted demo never executes an attack (automated test).

---

## 15. File map for implementers

| Path | Role |
|---|---|
| `content/areas/ai-security/` | Course 1 source of truth |
| `content/areas/blue-team/` | Course 2 (create) |
| `content/areas/web-appsec/` | Course 3 (create) |
| `content/areas/_template/` | Copy-paste for new Areas |
| `lab/content.py` | Loader — already multi-area |
| `lab/checks.py` | Add `http`, `file_contains`, `flag` |
| `lab/ui/catalog.html` | Honesty + Start per Area |
| `lab/ui/scenario.html` | Evidence column; Run vs Check |
| `lab/credential.py` | Issuer name → CyberRange |
| `docker-compose.yml` | Flagship AI stack |
| `docker-compose.web.yml` | Course 3 overlay (create) |
| `docker-compose.hosted.yml` | Public brochure (keep attack-free) |
| `tests/test_content_engine.py` | Gate for kinds + catalog |
| `docs/LEARN.md` | AI first-win (fix stale console URL) |
| `docs/LEARN-blue.md` / `LEARN-web.md` | Create at live flip |

---

## 16. Decision log (defaults if nobody debates)

1. **Start with one:** AI & Agent Security remains the only `available` Area until Blue meets the live bar.
2. **Second course:** Blue Team on the existing stack, not Web. Web is third because it needs new infra.
3. **Parallelism:** Kernel + AI polish + Blue authoring + Web spike in the same two weeks; only AI is “live.”
4. **No accounts** until three Areas are live.
5. **No malware/offensive envs** until isolation is designed (separate plan).
6. **Killercoda** is a funnel after the local first-win is clean, not a rewrite.

If you want Web as course 2 instead of Blue, swap §7 and §8; the kernel and live bar do not change. The parallel model does: Web cannot go live as fast as Blue.

---

## 17. One picture

```text
NOW                         TRAIN 1                      TRAIN 2
─────────────────────       ─────────────────────        ─────────────────────
Catalog                     Catalog                      Catalog
  ● AI Security (live)        ● AI Security                ● AI Security
  ○ Blue (hidden/authoring)   ● Blue Team (live)           ● Blue Team
  ○ Web (spike branch)        ○ Web (authoring)            ● Web AppSec (live)
  · 8 roadmap cards           · 8 roadmap cards            · 7 roadmap cards

Stack                       Stack                        Stack
  compose.yml (AI)            same                         compose.yml
                                                           + compose.web.yml
```

Start on the left. Parallel work fills the circles. Nothing on the right is claimed until it is green.
