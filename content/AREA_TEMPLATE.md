# Authoring an Area

One lesson engine, many courses. An Area brings content and an environment; it
never brings its own UI, its own progress model, or its own idea of what a check
is. If you find yourself needing a new check kind, that is an engine change —
raise it rather than working around it in markdown.

This file is the contract. `lab/content.py` is the parser; if the two disagree,
the parser wins and this file is out of date.

---

## Layout

```
content/areas/<area-id>/
  area.json                       # identity, environment, outcomes, credential
  scenarios/
    00-orientation/
      scenario.json               # ordered step list + metadata
      intro.md                    # shown above step 1
      step-01.md … step-NN.md
      checks/step-02.json         # optional, one per graded step
      finish.md                   # shown under the last step
  exploits/<id>.json              # optional: entries for the sandbox console
```

Folder names sort the scenarios on disk; `order` in `scenario.json` sorts them in
the catalog. Keep them consistent — a mismatch is confusing to everyone later.

---

## `area.json`

```json
{
  "id": "blue-team",
  "title": "Blue Team / SOC",
  "status": "authoring",
  "difficulty": "intermediate",
  "blurb": "One or two sentences. What you attack, what you build, what you measure.",
  "long_description": "A paragraph for the Area page.",
  "env": {
    "id": "blue-team",
    "compose": "docker-compose.yml",
    "services": ["agent", "mailhog"],
    "requires": ["docker"],
    "notes": "Reuses the AI stack. No new services."
  },
  "certs": ["frameworks this maps to — not exams you issue"],
  "roles": ["job titles a learner is aiming at"],
  "prerequisites": ["what they need before starting"],
  "outcomes": ["Verb-first. Six or fewer. Each one demonstrable in a scenario."],
  "credential": {
    "id": "…", "title": "…", "requires": "all scenarios completed", "description": "…"
  }
}
```

**`status` is the live gate.** Only `"available"` puts an Area in front of
learners. Use `"authoring"` while you write. Do not set `"available"` until the
Area meets the live bar in `docs/CYBERRANGE-PLAN.md` §3.

**`certs` are frameworks, not exams.** This project does not issue or proctor
industry certifications, and saying otherwise in an Area's metadata is the
fastest way to lose a learner's trust.

---

## `scenario.json`

```json
{
  "id": "01-triage-the-exfil",
  "title": "Triage the exfil you caused",
  "order": 1,
  "difficulty": "intermediate",
  "est_minutes": 18,
  "summary": "Two lines. This is what shows in the catalog table.",
  "owasp": ["LLM02:2026 Sensitive Information Disclosure"],
  "controls": ["C12 detection rule"],
  "takeaway": "The one sentence they should keep.",
  "steps": [
    { "id": "step-01", "title": "What you are looking at" },
    { "id": "step-02", "title": "Find the message" }
  ]
}
```

### `track` — which path the scenario belongs to

`core` (required for the badge), `persist` or `operate` in the AI Security Area, and
`reviewer` for the read-only officials track (no Docker, `recall` checks only, no
credential). The catalog builds its path cards from this field, so a missing value
puts the scenario in `core`.

### `legs` — optional trifecta legs

```json
"legs": ["u", "p", "e"]
```

Which legs of the lethal trifecta the scenario's attack path touches: `u` untrusted
content, `p` private data, `e` external communication. Leave it out when the path is
not about the trifecta. When present, the player shows the trifecta HUD in its header.
A leg lights only when a run actually travelled (`result.success`), so a secure-mode
run that held shows the legs dark. Unknown letters are dropped by `lab/content.py`.

### Playground ↔ scenario mapping

The browser playground (`lab/ui/play.html`) is the simulated front door. Each level
has a real counterpart in the range; keep them in step when either changes:

| Playground level | What it teaches | Range scenario(s) |
|---|---|---|
| L1 Watch the breach | indirect injection through retrieval, unscoped read, unrestricted send | `02-rag-poisoning`, `03-cross-tool-exfil`, `04-agent-exploit` |
| L2 Place the controls | egress allow-lists beat input filters; soft controls never count | `05-guardrail-map`, `17-data-guards` |
| L3 Find the composition cut | per-agent safety doesn't compose; property-flow cut at egress | `07-multi-agent` |
| L4 The tool lies | tool descriptions are untrusted content; pin manifests | `11-supply-chain`, `19-mcp-tool-poisoning` |
| Reviewer mode | the questions an approver asks | the `reviewer` track |

### `owasp` — always name the scheme

Write ids as **`LLM03:2026 Excessive Agency`**, not bare `LLM03`. The 2026 list renumbered
eight of ten categories and *swapped* LLM03 and LLM06 with their 2025 meanings, so a bare id
cannot be audited by reading — and a find/replace over bare ids silently inverts the files
that were already correct. `tests/test_owasp_2026_consistency.py` fails the build on any
id paired with its 2025 name.

### `difficulty` — four rungs, no synonyms

`beginner` · `intermediate` · `advanced` · `expert`. One ladder for the whole catalog, so
tiles from different Areas compare. Do not introduce `easy`/`medium`/`hard` — they were in
use once and meant the same three rungs under different names.

### Folder number vs `order`

The folder prefix is the **authoring id** and is permanent: it appears in check ids and in
saved learner progress, so renumbering a folder silently discards a learner's completions.
`order` is the **display position** and is free to change. They deliberately diverge — the
Core track puts `16-direct-injection` at position 2 — so read `order`, never the folder
number, when you need the sequence. Give a new scenario the next unused folder number and
set `order` to wherever it belongs in the path.

`legacy_id` is optional, and load-bearing when present: `lab/lessons.py` builds the
legacy `/lab/lessons` list from scenarios that declare one, and `simulate.py` and the
sandbox console depend on that list's contents and order. **Omit it** unless the
scenario really does answer to an older lesson id. Reusing another Area's simulation
(as Blue Team reuses `a3`) is not a reason to claim one.

---

## Steps

One `step-NN.md` per entry in `steps`. Write in the second person, lead with the
thing being done, and keep a step to one idea. Start the file with an `##`
heading — the scenario title is already on screen, so do not repeat it.

Inline the code you want read. "Open `agents/executor.py`" only works for someone
who already has the repo in an editor; fifteen quoted lines work for everyone.

---

## Checks — the part that matters

A step is graded when `checks/<step-id>.json` exists. **Run performs the work;
Check reads what happened.** Never write a check that performs the exercise on
the learner's behalf, and never write step copy that says the Check will run
something.

Available kinds:

| kind | asserts (grading mechanism) | use it for |
|---|---|---|
| `evidence` | the run the learner performed, via `lab/runlog.py` + the event log | every attack/defend step |
| `mailhog` | a matching message is (or is not) in the mail sink | exfiltration, egress controls |
| `recall` | an answer to a question, graded server-side | read-only steps, so Next-spam cannot reach 100% |
| `lab_status` | every tool server is reachable | one setup step per Area |
| `secure_mode` | the persistent container mode | rarely; prefer per-run mode |
| `simulate` | runs a simulation and asserts it | **do not use in new content** — it performs the exercise for the learner. It remains in the engine for compatibility only, and `tests/test_run_check_split.py` fails the build if content uses it. |

### The `asserts` field

Every graded check carries an `"asserts"` array in its JSON — 1 to 4 short strings,
one observable per entry, in the learner's language:

```json
"asserts": [
  "the agent ran db_tool and dumped more than one customer row",
  "an email left the agent and landed in the MailHog sink",
  "the message body contains customer data, not a summary"
]
```

Rules:

- **1 to 4 entries.** One observable per entry.
- **Present tense, lowercase start, no trailing period.** Read like a checklist
  item, not a sentence lifted from the code.
- **Name the observable state the check asserts** — rows returned, a message in
  the sink, an event on the timeline, the control that fired. Never "the script
  exits 0" and never an implementation detail nobody on screen would recognize.
- **Never spoil the answer.** For kind `recall`, the asserts describe what the
  question is testing ("you can name the control that stops a payload the
  allow-list would pass"), not the correct option's text. `_client_check()` in
  `lab/content.py` omits `asserts` from a recall step's payload entirely — the
  browser never sees it, same as `answer` — but the field is still required in
  the JSON so the convention holds for every graded check, and so a future kind
  that does ship it inherits a correct file to start from.
- **Match what the check actually asserts.** Read the check spec and, where it
  is not obvious, read the matching simulation in `lab/simulate.py`,
  `lab/sims_core.py`, `lab/sims_advanced.py` or `lab/sims_coverage.py` before
  writing. An assert that overstates the check is worse than no assert at all.

Two worked examples:

```json
// evidence — content/areas/ai-security/scenarios/03-cross-tool-exfil/checks/step-02.json
"asserts": [
  "db_tool dumped customer rows using an unscoped filter",
  "email_tool sent that dump to an external address in the same run"
]
```

```json
// recall — content/areas/ai-security/scenarios/18-agent-identity/checks/step-04.json
// (omitted from the client payload; still required in the file)
"asserts": [
  "you can name where the executor is required to source the customer_id from"
]
```

### `evidence`

```json
{
  "kind": "evidence",
  "simulate": "b1",
  "require_mode": "vulnerable",
  "expect": "success",
  "require_event": "sql",
  "event_contains": "WHERE 1=1",
  "pass_message": "What they proved, in their language.",
  "fail_message": "What to do next — never just 'failed'."
}
```

The step's **Run** button is derived from this: `simulate` becomes the run, and
`require_mode` becomes the mode it runs in. Do not also hand-write a `run` key
unless the step needs something the check cannot imply.

`expect` is `success`, `blocked`, or `ran`.

### `recall`

```json
{
  "kind": "recall",
  "prompt": "One question about what they just saw.",
  "options": ["…", "…", "…", "…"],
  "answer": 1,
  "pass_message": "Confirm the reasoning, do not just say 'correct'.",
  "fail_message": "Point at where the answer is — the timeline, not the prose."
}
```

`answer` never reaches the browser. Ask about something on screen (the SQL that
ran, which control fired), not about a definition they could guess.

### `mailhog`

```json
{
  "kind": "mailhog",
  "to_contains": "audit@external-logging.test",
  "subject_contains": "Customer Export",
  "expect_present": true,
  "pass_message": "…", "fail_message": "…"
}
```

---

## Messages

`pass_message` and `fail_message` are teaching surface, not log output. A pass
says what was proved. A failure says what to do next. Neither apologises.

---

## Environment

Reuse `docker-compose.yml` when the Area genuinely runs on the existing stack —
that is how a second course ships without a second product. A new environment
gets its own overlay (`docker-compose.<area>.yml`) and its own port range, and
**must not** appear in the hosted manifest.

## Before flipping `status` to `available`

Work through the live bar in `docs/CYBERRANGE-PLAN.md` §3. The short form: the
stack comes up clean, there is an orientation plus at least two graded
attack/defend scenarios plus a map, every check asserts real state, the evidence
is visible, tests exist, and the hosted surface still carries no attack tools.
