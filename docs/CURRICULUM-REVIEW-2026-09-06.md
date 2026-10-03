# Curriculum review — AI & Agent Security, Blue Team / SOC

> **Reviewer stance:** read as a cybersecurity practitioner assessing whether a stranger
> could hand this to a junior engineer and call it a course.
> **Date:** 2026-09-06 · **Reviewed:** `content/areas/` (23 scenarios, 15,363 words),
> `docs/AI-AGENT-SECURITY-CURRICULUM.md`, `docs/LEARN.md`, `docs/OWASP_COVERAGE.md`,
> `lab/credential.py`, `lab/ui/catalog.html`.
> **Companion:** [research prompt](research/CURRICULUM-RESEARCH-PROMPT.md) for the gaps this review cannot close from the repo.

---

## Status — updated 2026-09-08

| Finding | State | What was done |
|---|---|---|
| F1 ATLAS claim in the signed badge | **fixed** | Claim removed from `ai-security` `certs[]`. ATLAS technique mapping stays a research task; the badge no longer asserts training the content does not deliver. |
| F2 Blue Team missed the 2026 retag | **fixed** | `certs[]` and all four scenarios retagged, using the `LLMxx:2026 Name` form. |
| F3 `authoring` Area mints a credential | **fixed** | `credential.issue()` now refuses any Area whose `status` is not `available`, and says why. Verified live: `blue-team` refuses, `ai-security` still issues. |
| F4 `OWASP_COVERAGE.md` self-contradicting | **fixed** | Regenerated from `lab/curriculum.py` + the content tree. Real numbers: LLM **10/10**, ASI **7/10** (open: ASI05, ASI08, ASI09), 21 controls. The old file claimed 5/2/3. |
| F5 Paywalled syllabus cited to students | **fixed** | Both `intro.md` citations replaced with claims a learner can verify. |
| F13 `LEARN.md` six-layer map | **fixed** | Now the eight hops, and `G1` corrected to `A8`. |
| F14 `LEARN.md` loop omits Check | **fixed** | Loop rewritten around the Run/Check split, with "no run, no pass" stated. |
| F15 `LEARN.md` recreate contradiction | **fixed** | Section 4 marked optional and cross-referenced to the per-run switch. |
| F16 Check-runs copy | **fixed** | (Corrected earlier in the same pass.) |
| F17 folder number vs `order` | **documented, not renamed** | Renumbering folders would discard saved learner progress and break check ids, so the split is now an explicit rule in `AREA_TEMPLATE.md` instead. |
| F18 two difficulty scales | **fixed** | One four-rung ladder (`beginner`/`intermediate`/`advanced`/`expert`); 18 scenarios remapped; pinned by a test. |
| F19 missing `finish.md` | **fixed** | Written for `10-redteam-pipeline`; a test now fails the build if any scenario lacks one. |
| F20 Blue Team controls empty | **fixed** | `D1`–`D4` detection series added to `lab/curriculum.py` and cited by all four scenarios. |
| F6–F12 | **open** | Tier 2 is content authoring (a terminal assessment, deepening three thin labs, objectives, per-channel DLP grading), not defect repair. Sized separately. |

**Beyond the findings:** the 2026 renumbering turned out to be systemic, not confined to Blue
Team. Eight of ten ids changed meaning and LLM03/LLM06 *swapped*, so a bare id is unauditable
and a find/replace would have silently inverted the already-correct files. Every occurrence in
the repo was enumerated and classified by hand before any edit. Stale mappings were found and
fixed in `lab/curriculum.py` (`CONTROLS` C1–C16), `lab/sims_coverage.py` (including three sim
names the attack catalog renders), `defenses/m09`–`m11`, `docs/PRODUCT_FLOW.md`,
`docs/REMEDIATION.md`, `SECURITY_NOTES.md`, `FINDINGS-01.md`, and nine student-facing lesson
files. `tests/test_owasp_2026_consistency.py` now fails the build on any id paired with its
2025 name.

---

## Verdict

**The syllabus is professional. The delivery drifted from it.**

`docs/AI-AGENT-SECURITY-CURRICULUM.md` (2026-09-05) is a real syllabus: dependency-sequenced,
Core/Advanced split, an honest "what we are not" table, and market research that holds up under
spot-check — SANS SEC546 does exist as *Securing Agentic AI*, and its Section 1 (I/O boundaries,
prompt injection, identity and least privilege) and Sections 4–5 (browser/computer-use agents,
cyber-physical) match what the doc claims.

Six of that doc's nine implementation items landed:

| §10 item | State |
|---|---|
| 1–3. Add A5 data guards, A2 direct injection, A6 identity | Done |
| 4. Rewrite A8 guardrail map to eight hops | Done (`controls` now includes `C21`) |
| 5. Upgrade C1 `09-guardrails` to call A5's scanners | **Not done** |
| 6. Retag `owasp` arrays to 2026 IDs | Done for `ai-security`; **not done for `blue-team`** |
| 7. Set `order`; catalog groups by track | Done — `catalog.html` renders Core / Persistence / Operate headings |
| 8. Credential = Core graded checks only | Done (`requires_track: "core"`) |
| 9. LEARN.md first-win path = A0–A8 | Table done; **the rest of LEARN.md was not updated with it** |

So this is not a course that needs redesigning. It is a course whose **delivered artifacts have not
caught up with its own design**, and the places they lag are exactly the places a professional
reviewer looks first: the claims made to third parties, the terminal assessment, and the depth of
the labs the credential actually requires.

Findings are ordered by **who sees the defect**, not by file.

---

## Tier 1 — Claims a third party will read

These reach a hiring manager, a reviewer, or a badge verifier. They are the product's credibility.

### F1. The signed badge asserts MITRE ATLAS training that no lesson delivers — *critical*

`lab/credential.py` builds the assertion's framework list straight from the Area's `certs[]`:

```python
"criteria": {
    "narrative": (...),
    "frameworks": area.get("certs") or [],
},
```

`content/areas/ai-security/area.json` lists `"MITRE ATLAS (adversarial ML tactics)"`. A grep for
ATLAS technique identifiers across the whole content tree returns exactly one hit — that string
itself. **No `AML.T####` technique ID appears in any scenario, step, check, or `lab/curriculum.py`.**

The result: an HMAC-signed, Open Badges-shaped assertion tells a verifier the holder trained against
MITRE ATLAS, on the strength of a tile label. `credential.py`'s own docstring stakes the design on
being honest about what the badge proves; this is the one finding that undermines the artifact the
product exists to produce.

**Fix — conditional, and the condition is not yet known.** §1 of the research prompt asks whether
ATLAS in its current form even *has* honest techniques for agentic concerns (tool misuse, inter-agent
trust, agent identity) or remains centred on model-level attacks. That answer decides which branch:

- **If honest mappings exist:** put the technique IDs in `scenario.json`, surface them beside the
  OWASP chips, and keep the claim.
- **Otherwise — and this is the default until proven otherwise:** drop ATLAS from `certs[]`. OWASP
  LLM 2026 and ASI 2026 are genuinely earned and carry the tile on their own. Manufacturing a
  mapping to keep the label would reproduce the exact defect this finding is about.

### F2. Blue Team never received the 2026 retag — *high*

`content/areas/blue-team/` still carries 2025 numbering:

| Location | Says | 2026 reality |
|---|---|---|
| `01-triage-the-exfil`, `02-write-the-detection` | `LLM06 Excessive Agency` | LLM06 is **Unbounded Consumption**; Excessive Agency is **LLM03** |
| `00-orientation`, `01`, `03` | `LLM02 Sensitive Information Disclosure` (no year suffix) | Correct number, but unversioned while `ai-security` uses `LLM02:2026` |
| `blue-team/area.json` `certs[]` | `OWASP Top 10 for LLM Applications (2025)` | The reconstruction doc says explicitly: *"Drop 2025 from the tile."* |

Two Areas in one catalog citing two different editions of the same standard — with one of them
citing a number that now means something else entirely — is the most visible possible signal that
the mapping is decorative.

### F3. An `authoring` Area ships a mintable credential — *high*

`blue-team/area.json` has `"status": "authoring"` (correctly hidden from Available) yet carries a
full `credential` block: id `blue-team-triage`, title *Agent Incident Triage*,
`"requires": "all scenarios completed"` — and **no `requires_track`**. It also carries the stale
2025 `certs[]` from F2, which `credential.py` would copy into the assertion.

Four scenarios and six graded checks is not a credential. Either remove the block until the Area
meets the live bar, or gate it the way AI Security is gated.

### F4. `docs/OWASP_COVERAGE.md` contradicts itself and the running product — *high*

The header states: *"IDs below are the **2026** list (Excessive Agency is LLM03; Hidden Context
Exposure is LLM08)."* The table immediately below lists `LLM03 Supply Chain`, `LLM06 Excessive
Agency`, `LLM07 System Prompt Leakage` — the 2025 numbering. It then totals **"Full: 5 · Partial: 2
· Not yet: 3"** while the live `/lab/curriculum` endpoint reports `llm_top10_full: 10`.

The ASI table lists five IDs and stops. The closing section describes the product as *"Module 0–1
depth"* with multi-agent, guardrail pipelines, supply chain and jailbreak eval suites listed as
not-yet-built — all four of which now exist as scenarios 07, 09, 11 and 10.

This file is the one a reviewer opens to check the framework claim in F1. It currently reads as
though the coverage numbers were never real.

### F5. Student-facing copy cites a competitor's paid syllabus by sub-section — *medium*

`17-data-guards/intro.md` and `18-agent-identity/intro.md` cite `SANS SEC546 §1.4` and
*"SANS SEC546 opens with…"* in the lesson body.

To be clear about what is **not** wrong here: the course is real, and Section 1 genuinely covers
input/output boundary enforcement and agent identity/least-privilege — the research behind the
design doc was sound. The problem is placement and precision. A learner cannot verify `§1.4` without
paying SANS several thousand dollars; the citation borrows authority from a vendor with no
relationship to this project; and sub-section numbering in a commercial syllabus is not a stable
public reference.

**Fix:** lesson copy cites standards — OWASP ASI03, ATLAS techniques, NIST AI RMF. Competitor
syllabus analysis belongs in `docs/AI-AGENT-SECURITY-CURRICULUM.md`, where it already sits and is
appropriate.

---

## Tier 2 — Pedagogical structure

### F6. The course has no terminal assessment — *high*

`04-agent-exploit` describes itself in its own `summary` as **"The capstone"** — and sits at
`order: 7` of 19. The Core track actually ends on `05-guardrail-map` (order 8), whose final step is
titled *"The exam question"* and is a four-option `recall` check.

Core therefore terminates on **recognition**, not synthesis — that part is verified from the content
tree. The comparison is not: the courses this project benchmarks against are understood to end on an
unguided challenge (PortSwigger's practical exam, HTB Academy skills assessments, TryHackMe challenge
rooms), but their assessment *design* was not checked for this review. §3 of the research prompt is
what confirms it and turns it into a specification.

The design doc justifies A8's *position* (*"the map is useless until DLP and identity exist"*) — that
reasoning is right, and it says nothing about A8's suitability as a final assessment.

**Fix — cheapest version:** add one unguided step to A8, or an A9 challenge: *no walkthrough, no
named attack — restricted PII must reach MailHog, then must not, and the learner names which of the
eight hops they closed.* The `evidence` check kind already supports this; it asserts lab state, not
button presses.

### F7. The badge-required labs are the thinnest in the course — *high*

Measured, not asserted:

| Core scenario | Words | Claimed minutes |
|---|---:|---:|
| `04-agent-exploit` | 1,152 | 25 |
| `01-tool-abuse-sqli` | 1,021 | 15 |
| `02-rag-poisoning` | 801 | 15 |
| `05-guardrail-map` | 791 | 15 |
| `03-cross-tool-exfil` | 770 | 18 |
| `00-orientation` | 714 | 8 |
| **six original Core labs — mean** | **875** | |
| `17-data-guards` | 705 | 20 |
| `16-direct-injection` | 453 | 15 |
| `18-agent-identity` | **352** | 15 |
| **three added Core labs — mean** | **503** | |

The three labs added to close the 2026 coverage gap average **43% less content** than the six they
sit beside, and they are all **required for the credential**. `18-agent-identity` — the lab teaching
confused-deputy, arguably the single most transferable concept in the Area — is 352 words, and its
final step is 33 words:

> ## Put it on the map
>
> You now have DLP (what the data is) and identity (who it is for). The full-agent exploit next will
> need both, plus everything from SQLi and RAG.

That is a transition sentence, not a step. This is coverage-driven authoring: the labs exist because
`LLM01`, `LLM02` and `ASI03` needed a home, and it shows.

### F8. No lesson states a learning objective — *medium*

There is no `objectives` field anywhere in `content/`. What exists:

- `area.json` → `outcomes[]` (good, and well-written)
- `scenario.json` → `takeaway` — but a takeaway is a *conclusion*, delivered after the fact

A professional lesson opens by telling the learner what they will be able to do and how they will
know they did it. Right now a student entering `11-supply-chain` learns their objective only by
finishing it. This also blocks any future mapping to a skills framework (NICE, SFIA), because there
are no verb-form statements to map.

**Fix:** add `objectives: [...]` to `scenario.json` (2–3 measurable verbs each), render them above
step 1, and add the field to `content/AREA_TEMPLATE.md` so Blue Team and Web AppSec inherit it.

### F9. Time estimates are not calibrated to the work — *medium*

Core is 146 claimed minutes across 6,759 words. Assuming 200 wpm — a placeholder, and the reason §5
of the research prompt exists — that is ~34 minutes of reading, leaving ~112 minutes for roughly 20
Run/Check presses and reading their output. The whole Area claims 308 minutes for ~13,000 words. The
word counts are measured; only the rate is assumed.

Either the estimates are inflated 2–3x, or the labs are under-specified for the time they claim. Both
readings hurt a product whose pitch is *"you finish it on a laptop in an afternoon"* — a learner who
finishes Core in 50 minutes concludes the course was shallow, not that they were fast.

### F10. The DLP lab grades four channels with one composite check — *medium*

`docs/AI-AGENT-SECURITY-CURRICULUM.md` §5 is explicit: *"Four channels (must all be graded)"* —
input, context, output, tool. Delivered: `17-data-guards` has three checks, of which
`step-03.json` is a single `evidence` check on `simulate: data_guards, require_mode: secure,
expect: blocked`, with the pass message *"All four channels classified the payload and blocked or
masked it."*

One assertion covering four controls means a learner whose context channel leaks sees the same red
box as one whose output channel leaks, and cannot tell which. The lab's whole thesis is that the
channels are distinct.

### F11. The Advanced track duplicates Core instead of building on it — *medium*

Design doc §10 item 5: upgrade `09-guardrails` to call the A5 (C21) scanners and add one probe
labelled *content safety, not DLP*. Not done. `09-guardrails` still teaches its own inline regex set
under `C13`:

> The scanners catch: **input** — `ignore previous instructions`, `SYSTEM NOTE`, `filter=1=1` …
> **output** — email addresses outside your owned domain (PII egress) and secret patterns like `sk-…`

`controls` for that scenario is `["C13"]` — no `C21`. So a learner who just built data guards in A5
meets a second, unrelated scanner in C1 with no statement of how they relate. The measurement lab
should measure the control the learner already built. That connection is the reason the Advanced
track exists.

### F12. Twelve of nineteen scenarios are structurally identical — *low, but it is the "AI slop" tell*

`06`, `07`, `08`, `09`, `10`, `11`, `12`, `13`, `14`, `15` are each **exactly** 4 steps / 2 graded
checks / both `evidence` / the same 4-step arc *concept → attack → defend → prove*. The consistent
arc is a genuine strength — it is the pedagogy working. The *identical shape* is not: no scenario in
the Advanced tracks has a recall check, an optional step, a branch, or a different length, so the
second half of the course has no rhythm. Vary two or three deliberately.

---

## Tier 3 — Consistency and hygiene

| # | Finding | Where |
|---|---|---|
| F13 | `docs/LEARN.md` §5 still teaches the **six**-layer guardrail map — *"Six control layers (lesson G1): RAG trust, plan validation, schema, least privilege, HITL, tool policy"* — after A8 was rewritten to **eight** hops adding DLP and identity. It also still calls the lesson `G1`, a pre-migration id. | `docs/LEARN.md` §5 vs `05-guardrail-map` `controls: [C1…C7, C21]` |
| F14 | `docs/LEARN.md` §3's per-lesson loop is *"Read the story → Run simulation → Read SQL/plan/DEFENSE → Read takeaway"*. **Check is missing entirely** — stale against the Run/Check split, the fix the student feedback specifically asked for. | `docs/LEARN.md` §3 |
| F15 | `docs/LEARN.md` §2 states *"You do not need the container recreate to finish any scenario"*; §4, immediately after the lesson table, instructs the student to do exactly that recreate. A beginner reads §4 as the next required step. | `docs/LEARN.md` §2 vs §4 |
| F16 | `18-agent-identity/step-02.md` says *"**Check** runs that plan in vulnerable mode against the real database."* `content/AREA_TEMPLATE.md:113` forbids this in so many words: *"never write step copy that says the Check will run…"*. Only occurrence in the tree — the template is otherwise being followed. | one-line fix |
| F17 | Folder number no longer matches `order` for the three newest labs: `16-direct-injection` → order 2, `17-data-guards` → 5, `18-agent-identity` → 6. Display order is correct; the authoring tree is now misleading, and the next author will fight it. | rename and renumber, or document the split in `AREA_TEMPLATE.md` |
| F18 | Difficulty vocabulary is uncontrolled: `ai-security` uses `beginner`/`easy`/`medium`/`hard`; `blue-team` uses `beginner`/`intermediate`. Two scales in one catalog. | pick four labels, put them in `AREA_TEMPLATE.md` |
| F19 | `10-redteam-pipeline` has **no `finish.md`**. Every other scenario in both Areas has one, so the learner finishes that lab with no closing summary. | add it |
| F20 | Every `blue-team` scenario has `controls: []` while `ai-security` uses `C1`–`C21`. Detection engineering has controls too — log coverage, detection specificity, absence-of-evidence discipline — and they are taught in the copy; they are just not identified. | add a `D1`–`Dn` series to `lab/curriculum.py` |

---

## What is genuinely good (do not regress it)

- **`attack → defend → measure` is real and consistent.** Every scenario runs the attack against real
  SQL/SMTP/retrieval and then proves the same payload dies. Nothing in this course is a slide.
- **The dependency sequence is correct** and matches how SANS SEC546, TryHackMe and Microsoft Learn
  order the same material: foundations → tools → direct injection → indirect → data → identity →
  chain → map.
- **The honest-gaps table** (ASI05 RCE, ASI08 cascading failures, ASI09 human-agent trust, ML privacy,
  MLOps) is rarer than it should be and is a real differentiator. Keep publishing it on the Area page.
- **Blue Team's premise — "hunt the breach you caused"** — is the best pedagogical idea in the repo.
  It solves the problem every SOC course has (someone else's logs, someone else's attack) and it costs
  no new infrastructure. Its execution has the F2/F3 problems above; the idea is not one of them.
- **Grading asserts lab state, not exit codes.** Dumped rows, an intercepted message, the specific
  control that fired. That is the platform's actual moat and it is fully built.

---

## Recommended order of work

**Now — credibility, under an hour:** F1 ATLAS claim · F2 blue-team retag · F3 blue-team credential ·
F4 rewrite `OWASP_COVERAGE.md` · F16 one-line Check copy fix.

**Next — course quality:** F6 terminal challenge · F7 deepen `18`, `16`, `17` · F8 objectives field ·
F10 per-channel DLP grading · F11 wire C1 to C21.

**Then — hygiene:** F13–F15 LEARN.md rewrite · F5 recite standards not SANS sections · F17–F20.

**Needs outside research** — see [`research/CURRICULUM-RESEARCH-PROMPT.md`](research/CURRICULUM-RESEARCH-PROMPT.md):
ATLAS technique IDs per scenario (F1), NIST AI RMF / ISO 42001 / EU AI Act mapping (absent from
content entirely), terminal-assessment patterns (F6), objective verb conventions (F8), and
time-on-task calibration (F9).
