# Agent prompts — Tier A UI/UX advancement

> Three agents, partitioned by **file ownership** so none collide. This partition exists because of a
> standing rule on this project: *they should not all edit `catalog.html`.*
>
> Source of the work: [`UX-ADVANCEMENT-2026-09-07.md`](../UX-ADVANCEMENT-2026-09-07.md).
> Run all three in parallel. Agent 3 is the long pole — start it first if you stagger them.

---

## Shared preamble — paste at the top of every one of the three prompts

```text
PROJECT

CyberRange is a self-hosted, hands-on AI/agent-security training platform in
C:\Users\uddes\OneDrive\Desktop\cybersecurity\agentic-security-lab. A FastAPI app (agents/app.py)
serves a lesson engine over a deliberately vulnerable LangGraph agent stack in Docker: a planner and
executor, SQL / email / file tool servers, a Chroma RAG store, persistent memory, MailHog, Ollama.

Content lives in content/areas/<area>/ as the single source of truth. Two Areas:
ai-security (19 scenarios, 43 graded checks, live) and blue-team (4 scenarios, 6 graded, authoring).

Pedagogy on every scenario: attack -> defend (SECURE_MODE) -> measure. Grading asserts real lab
state -- rows dumped, mail intercepted, the specific control that fired -- never script exit codes.

The Run/Check split is load-bearing and must not regress: Run performs the attack; Check only
asserts the evidence that run left behind. "No run, no pass." lab/runlog.py enforces it, keyed on
(sim_id, require_mode, step_key). tests/test_run_check_split.py locks it. Never write UI or copy
that says Check will run, execute, fire, or perform anything.

FRONT END

Four static pages under lab/ui/, served by the app, no build step and no framework:
  catalog.html   -- Area index, groups scenarios by track (core / persist / operate)
  scenario.html  -- the stepper: lesson pane + evidence pane + Run/Check
  index.html     -- the sandbox console, free-fire attacks against the live agent
  verify.html    -- public badge verification
  cyberrange.css -- design tokens and shared primitives
  cyberrange.js  -- the CR namespace: CR.api, CR.esc, progress, the blast-trace renderer

Design system, already established -- follow it, do not redesign it:
  --ember  #ff6b35  the attack propagating
  --halon  #35e0c0  the control that contained it
  --void   #0a0c10  ground
  Space Grotesk (display) / Archivo (body) / JetBrains Mono (utility)
  4px spacing scale --s1..--s8
  .btn.attack = Run (ember).  .btn.assert = Check (halon).  .seg = the mode switch.

HARD CONSTRAINTS

1. The :root token block in cyberrange.css is FROZEN this pass. Do not add, rename or change a
   token. If you need a value that does not exist, use the nearest existing token and say so in
   your report. Page-specific CSS goes in that page's own <style> block -- the existing pattern.
2. The lab is deliberately vulnerable. It stays local-only, synthetic data, fake credentials, no
   real external targets. Never add a route, link or fetch to an external host.
3. Hosted safety: the hosted surface must never contain the terminal service, /run, /lab/attack/*,
   graded checks, ingestion routes, or /credential/{area_id}/issue. Do not touch SENSITIVE_PATHS
   in agents/app.py.
4. NEVER display fabricated data. No star ratings, no enrolment counts, no invented dates, no
   placeholder testimonials, no lorem ipsum. Every number on screen must be derived from real
   content or real lab state. If a number is not available, omit the element -- do not stub it.
   This is a hard product rule: the credibility of the completion badge depends on it.
5. Do not add ambient decoration -- no particle fields, starfields, drifting backgrounds,
   typewriter headline cycles, or marquee tickers. A previous pass deleted a scanline overlay for
   exactly this reason.
6. Do not reproduce copy from any other product. Patterns yes, strings never.
7. Responsive floor: works to 390px, no horizontal body scroll at any width, visible keyboard
   focus, prefers-reduced-motion respected.

VERIFY BEFORE YOU REPORT
  The stack is up at http://127.0.0.1:8000 (docker compose up -d if not; /health returns ok).
  Load the pages you changed and confirm the flows you touched actually work in the browser.
  Then run: python -m pytest tests/ -x -q
  tests/test_smoke.py::test_agent_end_to_end_with_tool_call is a known live-Ollama timeout --
  it may fail; nothing else may.

REPORT
  What you changed, file by file. What you verified and how. Anything you could not do and why.
  Do not report success for work you did not verify in a browser.
```

---

## The one contract the agents share

Agents 1 and 3 both touch the checks rubric. They build against this shape in parallel rather than
waiting on each other. **Agent 3 authors it; Agent 1 renders it and degrades silently when absent.**

```jsonc
// content/areas/<area>/scenarios/<scenario>/checks/step-NN.json
{
  "kind": "evidence",
  "simulate": "exfil_chain",
  "require_mode": "vulnerable",
  "expect": "success",

  // NEW this pass -- what Check will assert, in the learner's language.
  // One line per assertion. Present tense. Names the observable state, never the answer.
  // 1-4 entries. Must not spoil a recall answer.
  "asserts": [
    "the agent ran db_tool and dumped more than one customer row",
    "an email left the agent and landed in the MailHog sink",
    "the message body contains customer data, not a summary"
  ]
}
```

`_client_check()` in `lab/content.py` passes `asserts` through for every kind **except** `recall`,
where it is omitted entirely so the answer key cannot leak.

---

## Agent 1 — the scenario player

**Owns:** `lab/ui/scenario.html`, `lab/ui/cyberrange.js`
**Read-only:** everything else. Especially `catalog.html`, `content/**`, `lab/*.py`.

```text
[SHARED PREAMBLE]

YOUR SCOPE: lab/ui/scenario.html and lab/ui/cyberrange.js. You own these two files. Do not edit any
other file. catalog.html, area.html, content/** and lab/*.py belong to other agents working in
parallel right now -- editing them will collide.

Rebuild the scenario stepper into a dedicated lab player. Five changes.

1. PLAYER CHROME
   Drop the marketing header on this page only. Build a fixed left rail:
     - back link to the Area, brand mark, scenario title (truncate, title attribute for the full)
     - a circular progress ring showing graded-steps-passed / graded-steps-total
     - three counters in the style of the existing .tag: DONE, EVIDENCE, RECALL -- pass counts per
       check kind, read from the same localStorage progress CR already keeps
     - the step list, each entry carrying a TYPED EYEBROW above its title, derived from the step:
       READ (no check) / RUN + CHECK (has a run spec) / RECALL (kind recall) / LIVE (ungraded_live)
       and OPTIONAL where step.optional
     - a collapse toggle; collapsed state persists in localStorage
   Centre pane gets a position kicker in mono, e.g. "RUN + CHECK * STEP 3 OF 6".

2. THE CHECKS RUBRIC  <- the highest-value change in this pass
   Above the Run/Check buttons, add a collapsible disclosure: "N CHECKS" where N is
   check.asserts.length. Expanded, one row per assert: a status circle + the assert text.
   Circles are hollow before a check runs, halon and filled on pass, ember on fail.
   If check.asserts is absent (another agent is authoring them right now, in parallel), render
   nothing at all -- no empty box, no placeholder. Degrade silently.

3. GATE NEXT, WITH THE REASON INLINE
   On a graded step, Next is disabled until that step's check passes. Put the reason immediately
   beside the disabled control, in the same row -- not a tooltip, not a toast:
   "Pass the check to continue". Always render an explicit "Skip this step" text link beside it so
   the gate never traps anyone; a skipped step stays unpassed and still counts as missing for the
   badge. Read-only steps keep the existing Mark read button.

4. STATE-AWARE HELPER LINE
   One line under the action bar that states what to do next, before the learner clicks wrong:
     - stack not reachable -> "Start the lab stack to run this step."
     - stack up, nothing run -> "Run this step first. Check reads the evidence, it does not
       produce it."
     - run recorded, wrong mode -> name the mode this step grades
     - passed -> what it proved, one clause
   Take the state from GET /lab/status and from the existing check-response messages. Do not invent
   new server routes.

5. ENVIRONMENT PRE-FLIGHT PANE
   When the stack is not reachable, the evidence column becomes a composed panel, not a red pill:
   name the stack from the scenario payload's area.env (id, services, requires), state what will
   happen, list each service with its health as it comes up, and offer ONE copyable command.
   Be honest that we cannot start it for them -- it is their machine. No fake progress bar.

DO NOT
  - Do not change the Run/Check semantics, the runlog, or any check-response handling.
  - Do not write copy saying Check runs, executes or performs anything.
  - Do not touch the blast-trace containment logic in cyberrange.js -- isBlockingDefense() and the
    paintTrace result-row skip were bug fixes; leave them exactly as they are.
  - Do not remove the evidence column at any viewport. It must never be display:none. Under 1180px
    it reflows to one column and stacks below the lesson -- verify at 1440, 1180, 1024, 820, 390.
```

---

## Agent 2 — catalog and the new Area page

**Owns:** `lab/ui/catalog.html`, and a new `lab/ui/area.html`
**Read-only:** everything else. Especially `scenario.html`, `cyberrange.js`, `content/**`, `lab/*.py`.

```text
[SHARED PREAMBLE]

YOUR SCOPE: lab/ui/catalog.html, and one new file lab/ui/area.html. You own exactly these two. Do
not edit scenario.html, cyberrange.js, content/** or lab/*.py -- other agents own them and are
working in parallel right now.

The product currently has two levels, catalog -> scenario, so catalog.html is doing double duty as
both the index of Areas and the detail view of the one live Area. Split it into three.

1. NEW lab/ui/area.html?id=<area_id>
   The Area detail page. Everything it renders comes from GET /catalog -- the fields are already in
   the payload and nothing is currently using them.
     - breadcrumb: Range > <Area title>
     - title, icon, difficulty, status, long_description
     - a derived stat-chip row -- scenario count, total graded checks, estimated minutes, count of
       distinct check kinds. Every number computed from the payload. Never hard-code one.
     - outcomes[] -- "after this Area you can..."
     - prerequisites[] -- rendered as a checklist, not prose
     - the track sections (core / persist / operate) with the existing scenario table, moved here
       from catalog.html, each track showing its own count and minutes
     - the credential block: what it is, exactly what earns it (credential.requires_track), and a
       link to verify.html. Repeat the honesty line -- this instance signs its own badges.
     - a "Not covered by this Area" section. Render area.gaps[] if that key exists; if it does not,
       render nothing. Do not invent the list.
   Empty and loading states are authored, not defaults.

2. TRIM catalog.html BACK TO AN INDEX
   Area tiles only, linking to area.html. Adopt this card anatomy, which is standard for the
   category and which we currently lack:
     - mono kicker: "AREA * N SCENARIOS"
     - difficulty pill, colour-coded, top-right
     - description clamped to 3 lines
     - a composition line stating what kind of work is inside:
       "12 run+check * 5 recall * 2 read * ~308 min" -- all derived from the payload
     - the learner's own progress bar and percentage, from the same localStorage keys CR already
       uses (cr:progress:<area>:<scenario>)
     - status chip: available / authoring. Authoring tiles are visibly not enterable.
   Keep the existing hero. It animates a real breach reaching WORLD and then the same attack being
   contained -- it is subject-derived and it stays. Do not replace it with a typewriter or a
   particle field.

3. A CALLOUT PRIMITIVE
   Both pages need a left-accent note block for expectation-setting -- what the badge proves, what
   the Area does not cover, why an Area is still authoring. Build it once, in catalog.html's style
   block, in a form area.html can copy. Three tones using existing tokens only: halon (informational),
   brass (caveat), ember (warning).

4. FILTER, ONLY IF IT EARNS ITS PLACE
   If the scenario table on area.html exceeds one screen, add a filter input whose placeholder
   states the count ("Filter 19 of 19 scenarios..."). No faceted sidebar -- we have 23 scenarios,
   not 639. Skip this entirely if it does not earn the space.

DO NOT
  - Do not display ratings, enrolment counts, review counts, or any social proof. We have no users
    to count and inventing them is the one thing this product cannot do.
  - Do not hard-code any count. Every number is derived from /catalog at render time.
  - Do not mark blue-team available. Its status is authoring and that gate is deliberate.
```

---

## Agent 3 — check descriptions, the content contract, and the API

**Owns:** `content/areas/**/checks/*.json`, `content/AREA_TEMPLATE.md`, `lab/content.py`,
`tests/test_content_engine.py`
**Read-only:** all of `lab/ui/`, `agents/app.py`, `lab/runlog.py`, `lab/checks.py`.

```text
[SHARED PREAMBLE]

YOUR SCOPE: content/areas/**/checks/*.json, content/AREA_TEMPLATE.md, lab/content.py, and
tests/test_content_engine.py. Do not edit anything under lab/ui/ -- two other agents own those
files and are working in parallel right now. Do not edit lab/checks.py, lab/runlog.py or
agents/app.py; the grading path is correct and locked by tests.

You are the long pole. The player UI cannot show a learner what a Check will assert until you
author it.

1. AUTHOR "asserts" FOR ALL 49 GRADED CHECKS
   Add an "asserts" array to every graded check JSON across both Areas:

     "asserts": [
       "the agent ran db_tool and dumped more than one customer row",
       "an email left the agent and landed in the MailHog sink",
       "the message body contains customer data, not a summary"
     ]

   Rules:
     - 1 to 4 entries. One observable per entry.
     - Present tense, lowercase start, no trailing period. The learner's language, not the code's.
     - Name the OBSERVABLE STATE the check asserts -- rows, mail, an event line, the control that
       fired. Never "the script exits 0" and never an implementation detail.
     - Never spoil the answer. For kind "recall" the asserts describe what is being tested
       ("you can name the control that stops a payload the allow-list would pass"), not the option.
     - Must match what the check ACTUALLY asserts. Read the check spec and, where it is not obvious,
       read the matching simulate path in lab/simulate.py or lab/sims_core.py before writing.
       An assert that overstates the check is worse than no assert at all.

2. PASS IT THROUGH THE API
   Extend _client_check() in lab/content.py to include asserts for every kind EXCEPT recall, where
   it must be omitted so the answer key cannot leak. Keep the existing shape otherwise -- the
   scenario payload contract is relied on by a page you do not own.

3. DOCUMENT THE CONVENTION
   Add "asserts" to content/AREA_TEMPLATE.md's check-kind table with the rules above and two worked
   examples, one evidence and one recall, so Blue Team and the future Web AppSec Area inherit it.

4. TEST IT
   Extend tests/test_content_engine.py:
     - every graded check has a non-empty asserts array
     - no asserts entry exceeds a sane length (say 120 chars)
     - a recall check's client payload NEVER contains asserts or answer
     - the existing test that the answer key stays server-side still passes
   Do not loosen an existing assertion to make something pass. If a test fails, fix the root cause
   -- that is how the three failures in this file were fixed last time.

CONTEXT YOU WILL WANT
  Check kinds in use: evidence, recall, mailhog, lab_status. The "simulate" kind is deprecated and
  forbidden in new content -- a test enforces that.
  A yesterday review (docs/CURRICULUM-REVIEW-2026-09-06.md) found the three newest core scenarios
  (16-direct-injection, 17-data-guards, 18-agent-identity) are the thinnest in the course. Their
  asserts deserve extra care -- they carry the credential.
  While you are in 18-agent-identity/step-02.md you may fix one documented copy bug: it says
  "**Check** runs that plan in vulnerable mode", which content/AREA_TEMPLATE.md:113 explicitly
  forbids. Rewrite so Run performs and Check asserts. That is the only .md file you may touch.
```

---

## After all three land

They will have been working blind to each other. Before calling it done:

1. Load `catalog.html` → `area.html` → `scenario.html` and walk one full scenario end to end.
2. Confirm the rubric actually renders — Agent 1 degrades silently when `asserts` is missing, so an
   empty action bar means Agent 3's pass-through did not land.
3. Run the suite once more as a whole; the three agents each ran it against a different tree.
4. Check the responsive floor on all three pages at 390px.
5. Commit. The repo has one commit and a large dirty tree — this work should not be the second
   thing sitting uncommitted.
