# Research prompt — curriculum gap closure

> Hand the block below to a research agent (web access required). It is scoped to the five gaps
> [`docs/CURRICULUM-REVIEW-2026-09-06.md`](../CURRICULUM-REVIEW-2026-09-06.md) could not close from
> inside the repo.
>
> **Do not ask it to re-run the 2026-09-05 market survey.** That work exists in
> `docs/AI-AGENT-SECURITY-CURRICULUM.md`, was spot-checked against sans.org on 2026-09-06, and held
> up. Re-running it burns the agent's budget on a question already answered.

---

## The prompt

You are a cybersecurity curriculum researcher. Your output will be applied directly as patches to a
hands-on AI/agent-security training course, so it must be precise, sourced, and formatted for
mechanical application — not prose analysis.

### Context you are working against

A self-hosted training platform ("CyberRange") ships one live Area, **AI & Agent Security**: a real
LangGraph planner + executor, a SQL tool, an email tool, a file tool, a Chroma RAG store, persistent
memory, and MailHog — deliberately vulnerable, running in Docker on the learner's machine. Every
lesson follows **attack → defend (SECURE_MODE) → measure**. Grading asserts real lab state (rows
dumped, mail intercepted, which control fired), never script exit codes.

Nineteen scenarios in three tracks. **These folder names are the join key for every table you
produce — use them verbatim.**

| Folder | Order | Track | Title | Currently tagged |
|---|---:|---|---|---|
| `00-orientation` | 0 | core | What is an agent with tools? | — |
| `01-tool-abuse-sqli` | 1 | core | Tool abuse — SQL injection (no LLM needed) | LLM03:2026, ASI02 |
| `16-direct-injection` | 2 | core | Direct prompt injection & jailbreak | LLM01:2026, LLM03:2026 |
| `02-rag-poisoning` | 3 | core | Poison the LLM context (RAG) | LLM01, LLM05, LLM09, ASI06 |
| `03-cross-tool-exfil` | 4 | core | Cross-tool exfiltration (dump → email) | LLM02, LLM03, ASI02 |
| `17-data-guards` | 5 | core | Data guards — DLP for agents | LLM02, LLM10, ASI03 |
| `18-agent-identity` | 6 | core | Agent identity & confused deputy | ASI03, LLM03 |
| `04-agent-exploit` | 7 | core | Exploit the agent (RAG → planner → tools) | LLM01, LLM03, ASI01, ASI02 |
| `05-guardrail-map` | 8 | core | Guardrail map — what to build and where | all Core IDs |
| `06-rag-deep-poisoning` | 9 | persist | Deep RAG poisoning — crowding & false provenance | LLM01, LLM05, LLM09, ASI06 |
| `08-memory-poisoning` | 10 | persist | Memory poisoning — the persistent backdoor | ASI06, LLM01, ASI01 |
| `07-multi-agent` | 11 | persist | Multi-agent attacks — tampering & rogue agents | ASI07, ASI01, ASI10 |
| `11-supply-chain` | 12 | persist | Supply chain — rogue tools & MCP servers | LLM04, ASI04, ASI10 |
| `09-guardrails` | 13 | operate | Production guardrails & observability | LLM01, LLM02, LLM10 |
| `10-redteam-pipeline` | 14 | operate | Red-team evaluation pipeline | LLM01, LLM02, LLM03 |
| `12-governance` | 15 | operate | Governance & policy-as-code | LLM03, ASI03 |
| `13-prompt-leakage` | 16 | operate | System prompt leakage | LLM08:2026, LLM01 |
| `14-grounding` | 17 | operate | Misinformation — groundedness & citations | LLM07:2026, LLM05 |
| `15-resource-limits` | 18 | operate | Unbounded consumption — denial of wallet | LLM06:2026 |

A second Area, **Blue Team / SOC** (`status: authoring`), has four scenarios — `00-orientation`,
`01-triage-the-exfil`, `02-write-the-detection`, `03-prove-the-control` — in which the learner works
the incident they themselves caused in `03-cross-tool-exfil`, using the lab event log and the
MailHog sink as the only evidence surfaces.

Explicitly **out of scope** for this course, and to stay out of your recommendations: model-level ML
security (membership inference, model inversion, extraction, adversarial perturbation), MLOps
platform security (SageMaker, Airflow, Kubernetes, pickle deserialization), browser and
computer-use agents, and cyber-physical/robotics agents.

### Your five deliverables

Answer each as its own section. Every section ends with its own source list.

---

**1 — MITRE ATLAS technique mapping (highest priority)**

The Area tile claims *"MITRE ATLAS (adversarial ML tactics)"* as a framework, and that string is
copied into a signed completion badge. No ATLAS technique ID appears anywhere in the content. Either
back the claim or it gets dropped.

From the current live ATLAS matrix at <https://atlas.mitre.org/>:

- Produce a table: **folder name → ATLAS tactic → technique ID (`AML.T####`) → technique name → one
  sentence tying it to what that specific scenario has the learner do.**
- Prefer one or two techniques per scenario. Do not pad. If a scenario has no honest ATLAS mapping,
  write `none` and say why — that answer is as useful as a mapping.
- Flag any technique ID that has been deprecated, renumbered, or superseded, with its replacement.
- State separately whether ATLAS in its current form covers **agentic** concerns (tool misuse,
  inter-agent trust, agent identity) or remains centred on ML-model attacks. If the latter, say so
  plainly — a recommendation to drop the claim is an acceptable and valuable outcome.

**2 — Governance framework mapping**

No content in this repo references NIST, ISO or the EU AI Act. `12-governance` teaches policy-as-code
and audit trails with no external anchor.

For each of **NIST AI RMF 1.0** (plus the Generative AI Profile, NIST AI 600-1), **ISO/IEC 42001**,
and the **EU AI Act**:

- Which specific functions, subcategories, clauses or articles are actually exercised by hands-on
  work in this course? Cite the identifier (e.g. `GOVERN 1.1`, `MEASURE 2.7`, Annex A control number,
  Article number).
- Give a folder → identifier table on the same join key as §1.
- Say which of the three is worth adding to the Area tile's `certs[]`, and which would be an
  unbacked claim of the same kind this review just flagged. **Recommending "none of them, not yet"
  is a valid answer** — argue it if that is what the evidence supports.
- Note any compliance-date changes to the EU AI Act that affect how a 2026 course should describe it.

**3 — Terminal assessment patterns**

Core currently ends on a four-option recall question. It needs an unguided challenge.

Research how comparable hands-on security courses construct a **summative** assessment, and what
makes one gradeable without step-by-step guidance:

- PortSwigger Web Security Academy — mystery labs and the BSCP practical exam
- Hack The Box Academy — end-of-module skills assessments
- TryHackMe — challenge rooms at the end of a path
- Any published assessment design for AI/LLM security specifically

For each: how is the task framed (goal-only? scenario brief? time limit?), what is the pass
condition, how is guidance withheld without making the task unfair, and how are hints or partial
credit handled.

Then give **one concrete proposal** for this course's terminal challenge, in this shape: the brief
the learner sees, the pass condition expressed as **lab state** (rows in the DB, a message in
MailHog, a named control in the event log — not "the script exited 0"), and what the learner must
articulate to pass. It must be completable with the existing stack: no new Docker services.

**4 — Learning-objective conventions**

No scenario declares objectives. A field is being added.

- What verb taxonomy do professional security curricula actually use for hands-on lab objectives?
  Compare Bloom's revised taxonomy against what SANS course pages, NICE Framework task statements
  (NIST SP 800-181r1), and vendor course pages publish. Note where they diverge.
- How many objectives per 15–25 minute hands-on lab is standard?
- Give **five worked examples** rewriting existing `takeaway` strings into objective form. Use the
  real strings, and label each with its folder. For instance, `18-agent-identity` currently has:
  *"The agent's service identity is not the user's authorization. Scope comes from the session
  principal."*
- State the difference you are applying between an objective (before, measurable, verb-form) and a
  takeaway (after, conclusion) in one or two sentences.

**5 — Time-on-task calibration**

The Area claims 308 minutes across ~13,000 words of lesson text. The Core track claims 146 minutes
across 6,759 words — roughly 34 minutes of reading plus about 20 button presses and their output.

- What published data exists on realistic completion times for hands-on security labs, and what
  ratio of reading to doing do platforms assume? Prefer platform-published estimates (TryHackMe room
  times, HTB module hours, PortSwigger lab estimates) and any instructional-design research on
  time-on-task for technical labs.
- Give a defensible **words-and-interactions → minutes** heuristic.
- Apply it to the 19 folders above and return a table: **folder → current `est_minutes` →
  recommended `est_minutes` → the delta and why.** Word counts per scenario are available in the
  review document; ask for them if you need them rather than guessing.
- State whether the honest conclusion is *the estimates are inflated* or *the labs are thin for the
  time claimed* — these have opposite fixes, and picking the wrong one makes the course worse.

### Rules — all five sections

1. **Cite a URL for every factual claim.** No source, no claim.
2. **Separate verified from inferred.** Mark each row or claim `[verified: <url>]` or
   `[inferred: <reasoning>]`. Do not blur the two. An inference clearly labelled is useful; an
   inference presented as fact is a defect.
3. **Never reproduce paywalled syllabus internals.** Public course *outlines* are fair to cite.
   Do not quote or reconstruct section numbering, lab instructions, or exam content from a paid
   course. If a claim can only be supported by paywalled material, say so and leave it unsupported.
4. **Patch-ready output.** Tables keyed to the folder names above, not narrative. A human should be
   able to read a row and edit one `scenario.json` from it.
5. **Say "no" when the evidence says no.** Recommending that a framework claim be dropped, or that a
   mapping does not honestly exist, is a successful outcome. Do not manufacture coverage — a
   fabricated mapping in this course would reproduce the exact defect that prompted this research.
6. **Flag anything that has changed since mid-2026.** Standards in this space renumber; OWASP's LLM
   Top 10 already did so in August 2026. Note publication and revision dates for everything you cite.
