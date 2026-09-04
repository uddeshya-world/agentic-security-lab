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
  "owasp": ["LLM02 Sensitive Information Disclosure"],
  "controls": ["C12 detection rule"],
  "takeaway": "The one sentence they should keep.",
  "steps": [
    { "id": "step-01", "title": "What you are looking at" },
    { "id": "step-02", "title": "Find the message" }
  ]
}
```

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

| kind | asserts | use it for |
|---|---|---|
| `evidence` | the run the learner performed, via `lab/runlog.py` + the event log | every attack/defend step |
| `mailhog` | a matching message is (or is not) in the mail sink | exfiltration, egress controls |
| `recall` | an answer to a question, graded server-side | read-only steps, so Next-spam cannot reach 100% |
| `lab_status` | every tool server is reachable | one setup step per Area |
| `secure_mode` | the persistent container mode | rarely; prefer per-run mode |
| `simulate` | runs a simulation and asserts it | **do not use in new content** — it performs the exercise for the learner. It remains in the engine for compatibility only, and `tests/test_run_check_split.py` fails the build if content uses it. |

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
