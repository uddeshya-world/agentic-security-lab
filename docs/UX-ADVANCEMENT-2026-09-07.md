# UI/UX advancement program — derived from an escbash.com teardown

> **Date:** 2026-09-07 · **Reference:** [escbash.com](https://www.escbash.com/) — a launched, hands-on
> DevOps/Linux lab platform with the same product shape as CyberRange (catalog → course → stepped
> lessons beside a live machine, per-step grading, completion credential).
> **Screens walked:** homepage, `/skills`, `/skills/linux`, `/catalog`, `/roadmaps`,
> `/certifications`, `/leaderboard`, `/pricing`, the sign-in wall, and the lab player
> (`/topics/linux-shell-basics`) including a hands-on task with its checks rubric expanded and the
> Terminal / Editor / Scratchpad panes.
> **Not signed in.** Everything below is the signed-out surface.
> **Companion:** [agent prompts](research/UI-AGENT-PROMPTS.md).

---

## The decision this list is built on

CyberRange stays **self-hosted, single-user, localStorage progress, free-OSS-first** — the
invariants in `docs/CYBERRANGE-PLAN.md` hold. That partitions everything escbash does into three
buckets, and the partition is the point of this document.

Yesterday's curriculum review found the product's worst defect was asserting MITRE ATLAS coverage it
had not earned. An advancement list that says *"add star ratings and enrolled counts"* is that same
defect wearing a new coat. So each item below is filed as **Portable now**, **Parked**, or **Never**,
and the Never items carry a reason so they don't get re-proposed next quarter.

---

## Scope of this pass

**In:** the three existing pages, a rebuilt scenario player, and one new page.

**The new page is `area.html`, and it is structural rather than cosmetic.** escbash runs three
levels — catalog → skill detail → topic player. CyberRange runs two — catalog → scenario. Our
`catalog.html` is therefore doing double duty as both the index of Areas and the detail view of the
one Area that is live, which is why `area.json`'s `outcomes`, `prerequisites`, `long_description`
and the honest-gaps table have nowhere good to live. Splitting that out is the single change that
most makes the product read as finished.

**Out, deliberately:**

| Not doing | Why |
|---|---|
| Faceted catalog sidebar with type/category counts | escbash needs it for 639 items. We have 23. YAGNI. |
| Global search | Same. Revisit past ~60 scenarios. |
| A separate certifications index page | We have one credential. It belongs on `area.html`, next to what earns it. |
| Grid/list view toggle | Two ways to render 23 rows is a setting, not a feature. |
| Rebuilding the design tokens | `cyberrange.css` `:root` is frozen this pass. The palette is not the problem. |

---

## Bucket 1 — Portable now

### Tier A — the finished-product signal

These six are what separates "a working app" from "a product". Do them first.

#### A1. Show the checks rubric before the learner submits — *highest value on the list*

**Seen:** a hands-on task's action bar carries a collapsible `▸ 6 CHECKS` disclosure. Expanded, it
lists one plain-language line per check, each with a hollow status circle:

```
- 6 CHECKS
  ○ /root/answers directory exists
  ○ user.txt contains your username
  ○ host.txt contains the machine hostname
  ○ kernel.txt says Linux
  ○ root-listing.txt lists the top-level folders
  ○ os.txt identifies the operating system
```

**Why it matters here:** the learner reads the rubric *before* attempting, and a failure points at
one line rather than turning the whole step red. This is the direct answer to the student feedback
that Check behaved like a skip button, and it is the missing half of the Run/Check split we already
built — we made Check honest, but we never told the learner what it was going to assert.

**The cost, stated plainly, because it is not a UI-only change.** `_client_check()` in
`lab/content.py` ships only `kind`, `require_mode` and `expect` (or `prompt`/`options` for a recall).
There is no human-readable description to render, and `pass_message` would spoil the answer. So this
needs:

1. a new `description` (or `asserts[]`) key authored into **all 49 graded `checks/*.json`**,
2. `_client_check()` extended to pass it through,
3. an entry in `content/AREA_TEMPLATE.md` so Blue Team and Web AppSec inherit the convention,
4. the disclosure UI itself.

Three of those four are content and API work, not front-end. Plan accordingly.

#### A2. Gate Next, and put the reason beside the disabled control

**Seen:** the action bar reads `← Previous` · *"Pass the checks to continue"* · `Next task →`
(disabled) · `Submit`. The reason sits inline with the control it explains — not in a tooltip, not
in a toast after a failed click.

**Here:** graded steps currently do not gate progression at all. A learner can walk the whole Core
track without passing anything and still see the badge dialog explain what is missing — the
correction arrives at the end instead of at the step. Gate `Next`, state why inline, and keep an
explicit "skip this step" escape so the gate never traps someone.

#### A3. Give the player its own chrome

**Seen:** the topic page drops the marketing nav entirely. A fixed, collapsible left rail carries:
back arrow · brand · truncated topic title · a **circular progress ring** · three per-type counters
(`0 DONE` / `0/2 QUIZZES` / `0/2 TASKS`) · the step list · theme toggle · three layout presets.
The centre pane has a `LESSON · 1 OF 9` position kicker.

**Here:** `scenario.html` still wears the site header. Adopt: collapsible rail, progress ring,
position kicker, and per-type counters mapped to our kinds — **DONE / EVIDENCE / RECALL**. Drop the
layout presets (low value at our pane count).

#### A4. Design the environment pre-flight state

**Seen:** before the machine is up, the right pane is a designed surface, not an error:

> `>_`
> Spin up a fresh environment and practice live.
> `linux-devops-basic · fresh machine · ready in under a minute`
> **`>_ Start Lab`**

It names the environment, sets a time expectation, and gives one button.

**Here:** this is our single best onboarding win. Docker-not-running is currently a red status pill
and a wall of shell commands — the exact friction the student feedback flagged. Replace it with a
first-class pane: name the stack from `area.json`'s `env` block, state what will happen, show the
health of each service as it comes up, and offer the one command to copy. Our version cannot spin
the stack up for the user (it is their machine), and it should say so rather than pretending.

#### A5. Build `area.html` — the missing level

**Seen:** `/skills/linux` is a real page — breadcrumb, title, description, a derived stat chip row
(`22 topics · 41 hands-on tasks · 21 quizzes · ~753 min`), and a **vertical connected stepper rail**
where each step is a node on a spine, the current one ringed, later ones locked.

**Here:** one page per Area carrying `long_description`, `outcomes`, `prerequisites`, the track
grouping we already render, the credential and what earns it, and — this is ours, not theirs — the
**honest-gaps table** (ASI05, ASI08, ASI09, ML privacy, MLOps). Publishing what the course does
*not* cover, on the course page, is a differentiator no competitor on this list attempts.

#### A6. Tell the learner what kind of work is in each step

**Seen:** every step in the skill rail carries a composition line —
`▶ 5 concepts · ▤ 2 tasks · ? 2 quizzes · 40 min` — with an icon per content type, and every step in
the player rail carries a typed eyebrow (`LESSON` / `TASK`).

**Here:** this is the cure for review finding F12, where twelve of nineteen scenarios are
structurally identical and the second half of the course has no rhythm. We already have the data —
`check_kind` per step, `run` spec, `ungraded_live`, `optional`. We simply never surface it. Render
per-step types in the rail and a composition line per scenario in the catalog.

### Tier B — substance, after Tier A

| # | Pattern seen | What we do with it |
|---|---|---|
| **B1** | Course card anatomy: mono kicker `COURSE · 128 LESSONS`, colour-coded difficulty pill, 3-line clamped description, `topics 22`, inline progress bar + `0%` + action button, `NEW` badge, category header with count (`DEVOPS · 9`) | Adopt the whole anatomy minus ratings and enrolment. Our progress data already exists in localStorage. `NEW` is honest for us — content dates come from git. |
| **B2** | Right pane is tabbed **Terminal 1 / Editor / Scratchpad**, and an unavailable tab is **greyed in place, not hidden** | Ours becomes **Timeline / Evidence / Notes**. The greyed-not-hidden rule is the transferable part: a learner should see that a surface exists and why it is unavailable. |
| **B3** | The Certifications page ships **one** certification and still reads finished, because the subtitle states provenance: *"600 original practice questions across 1 certification — written in-house against the official blueprints, no dumps."* Plus a left-accent callout bar setting expectations. | Honest scale beats fake breadth — exactly review finding F3. Adopt the provenance-subtitle pattern and build the callout as a shared component; our badge caveat and "what this course does not cover" both want it. |
| **B4** | Homepage embeds a real recorded run inside fake terminal chrome (traffic-light dots, titled *escbash live demo*), with a mute control | A canned replay of a scenario run. This is what `docker-compose.hosted.yml` needs anyway — the hosted surface has no attack tools by design, so a replay is the only honest demo it can carry. |
| **B5** | Theme toggle in the nav; both themes are first-class | We are dark-only. The tokens are already centralised in `cyberrange.css`, so a light theme is a token-layer change plus an audit, not a rewrite. |
| **B6** | The catalog's filter input states the count in its own placeholder: *"Filter 639 of 639…"* | Cheap, and it makes an empty filter result self-explanatory. |

### Tier C — principles, not features

Two things escbash does that cost nothing to copy and improve the product more than most features:

- **Write every rule on the page.** The leaderboard states its point threshold (100 to appear), its
  tie-break (whoever reached the score first), and its exact reset times. We already do this for the
  badge — `credential.py` says what the signature proves and does not prove. Extend the same
  discipline to graded checks, mode gating, and progress storage.
- **Design every degraded state.** Their signed-out leaderboard is a composed panel, not a blank.
  Their Scratchpad renders a real message and a Retry when it cannot load. Our loading, empty,
  Docker-down and check-failed states should all be authored, not defaults.

---

## Bucket 2 — Parked (needs accounts or infrastructure we chose not to build)

Named honestly, so nobody re-litigates them by accident.

| Feature | What it needs | Revisit when |
|---|---|---|
| Leaderboard, points, streaks, titles, "firsts", seasons | Accounts, a server, a shared database | Only if hosting is on the table |
| Progress that follows you across devices | Same | Same |
| "My Lab Sessions" — running-environment management | A server that owns the containers. Ours run on the learner's own machine. | Probably never, by design |
| Enrolment, and the enrol/resume state on a card | Accounts | With accounts |
| Audio narration per lesson (`▶ Explain this lesson · 1:46`) with language selection | A TTS pipeline and hosted audio. Not account-gated, but real infrastructure. | Genuinely good; treat as its own project |
| Ratings, review counts | Accounts **and** a real user base | See Bucket 3 |
| Pricing tiers, PRO gating | A business model we have not chosen | Out of scope for free-OSS-first |
| Discord / community | A community | When there is one |

## Bucket 3 — Never

| Pattern | Why not |
|---|---|
| Star ratings (`4.8 ★ · 1,314 ratings`) | We have no raters. Displaying a rating we invented is fabricated social proof — the exact class of defect the curriculum review flagged as critical yesterday. |
| Enrolment counts (`6,856 enrolled`) | Same. Their number ticked up by one between two page loads; it is live. Ours would be a literal. |
| "Published Jul 2026" as decoration | Fine **only** because our dates are real and come from git. Never hand-write one. |
| Ambient starfield / drifting particle background | Decoration unrelated to the subject. We already deleted a scanline overlay for this reason. |
| Typewriter hero cycling job titles, and the horizontal marquee of lab names | Both are the current generic-AI-site vocabulary. Our hero already animates a real breach reaching WORLD and then being contained — subject-derived, and strictly better. Do not replace it. |

---

## Sequence

1. **A1 content half first** — 49 check descriptions plus the `AREA_TEMPLATE.md` convention. It is
   the long pole and everything in the player action bar depends on it.
2. **A3, A2, A4, A6** — the player, in that order. A3 creates the chrome the rest live inside.
3. **A5** — `area.html`, then trim `catalog.html` back to being an index.
4. **B1, B3, B6** — card and copy work across catalog and area.
5. **B2, B5, B4** — panes, light theme, recorded demo.

Tier A is the pass that makes it read as finished. Tier B is what keeps it reading that way on the
second visit.

---

## A note on sourcing

Every pattern above was observed on escbash.com on 2026-09-07 and is recorded here as a *structural*
observation — layout, information hierarchy, state handling. **No copy is to be reproduced.** Their
voice is not ours: they write for a DevOps learner buying a track; we write for a security engineer
who needs to trust what a badge asserts. Where this document quotes their wording it is to identify
the pattern, never to supply the string.
