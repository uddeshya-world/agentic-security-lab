# Launch plan — why anyone should stop scrolling for this lab

*Written 2026-10-03. Companion to the review of the same date.*

## 1. The honest question: is another lab relevant?

Not as "another vulnerable lab". That shelf filled up in 2025–26:

| Offering | Form | You play | Defense taught? | Cost / friction |
|---|---|---|---|---|
| Lakera Gandalf · Agent Breaker | Browser game, 10 mock agent apps | Attacker | Lakera's guardrails, as a black box you try to beat | Free, zero install |
| Damn Vulnerable AI Agent (OpenA2A) | Docker one-liner, 21 agents, 22 CTFs, MCP + A2A | Attacker | Links out to the vendor's own hardening tools | Free, Docker |
| AIGoat, DEF CON / c0c0n trainings | Docker labs + instructor | Attacker, some defense | Yes, in class | Paid seat, travel |
| Practical DevSecOps CMCPSE | 60-day lab + 6-hour exam | Attacker + MCP threat model | Yes | $599 |
| fanout.sh labs | Browser, structured paths, "Agent Control Room" | Operator configuring an agent | Configuration, not attacks | Free tier, zero install |

What nobody ships:

1. **You as the defender who has to choose.** Every CTF scores a break. None
   scores *where you put the stop and what it cost*.
2. **Proof, not a vibe.** Same payload, control on, named control fires, graded
   on real state. The full lab already does this. It is the strongest thing it has.
3. **Composition.** Three agents that each pass a per-agent check can still close
   the trifecta through a shared store. That is MESA's INV-01, and no lab teaches it.
4. **A public-sector frame.** Citizen records, helpdesk agents, public-edit
   knowledge bases. This is the audience the newsletter already reaches.

**Position:** *Everyone teaches you to break the agent. CyberRange makes you
decide where the control goes — and proves it.*

## 2. What fanout.sh gets right, applied here

| fanout pattern | What it means for us | Done |
|---|---|---|
| One link, no install, no signup | `lab/ui/play.html`, fully client-side | ✓ |
| First value inside a minute | Level 1 hop 6 lands the breach in ~6 clicks | ✓ |
| Structured paths, visible progress | 3-level rail with done state, persisted locally | ✓ |
| Labs are *instruments* you operate, not pages you read | Budget meter, control toggles, closure vector | ✓ |
| A reason to come back | Share card + "go deeper" into the Docker range | ✓ (v1) |

## 3. What makes it demanding (the stop-scroll ingredients)

- **A constraint.** A budget of 3 points. With no constraint, people tick
  every box and learn nothing. The optimum (2 points, both egress allow-lists)
  is the lesson: many ways in, few ways out.
- **Controls that lie.** Brass controls (classifier, spotlighting, row limits)
  lower odds but don't count as a stop. People pick them first, watch them fail,
  and remember why.
- **A wrong answer that looks right.** In Level 3, "firewall the reporting agent"
  gives (1,1,0) and still fails, because it breaks the service.
- **One number to screenshot.** `(1, 1, 1) → (1, 1, 0)`. That is the post.
- **A share line with a score in it.** "3 of 3 stopped with 2 points." Scores
  get compared, and comparison drives clicks.

## 4. Sequence

**Week 1 — ship the front door**
- [x] `lab/ui/play.html` (also published as a standalone link)
- [x] Catalog CTA: "New here? Play the 15-minute version"
- [ ] Host `play.html` on a public static URL (GitHub Pages or Cloudflare Pages).
      It is safe to host: no backend, no model, synthetic data.
- [ ] Newsletter edition: lead with the Level 3 screenshot, link the page

**Week 2 — make the repo match the folder**
- [x] Per-install random signing key; server-side pass ledger (`lab/ledger.py`)
- [x] `token.txt`, key and ledger in `.gitignore`; CI runs on `master`
- [x] README / ROADMAP / LEARN contradictions fixed
- [ ] Commit the 56 untracked files (Core labs 16–18, `lab/sims_core.py`,
      2026 OWASP tests). A clone today gets a different course.
- [ ] Move `feedback.txt` to `docs/research/` or out of the public repo
- [ ] Push to a public remote and confirm the red-team workflow goes green

**Week 3–4 — deepen what only we have**
- [ ] Level 4 in the playground: MCP tool-description poisoning, cut at the
      tool registry (ASI04), matching scenario 11 in the range
- [ ] Map the Level 3 policies to the OWASP Agent Control Standard's
      enforcement points once its spec is stable
- [ ] Officials track: a 20-minute "walk-through for a review committee"
      version of Levels 1–3 with a printable one-page checklist
- [ ] Hosted issuer (only if the badge needs to mean something to a third
      party): a key you hold, with the self-hosted badge kept as "completion record"

## 5. How we'll know it worked

| Signal | Target, first 30 days |
|---|---|
| Playground completions (all 3 levels) | 500 |
| Share-card copies | 15% of completions |
| Click-through to the Docker range | 10% of completions |
| Repo stars | 150 (DVAA sits near 110) |
| Inbound from public-sector or training orgs | 3 conversations |

Measure with a privacy-respecting counter on the hosted page only (no tracking
inside the local lab).

## Sources

- Lakera, *Agent Breaker* — https://www.lakera.ai/blog/gandalf-agent-breaker
- NHI Mgmt Group on Agent Breaker — https://nhimg.org/articles/agent-breaker-shows-how-genai-security-testbeds-model-real-attacks/
- OpenA2A, Damn Vulnerable AI Agent — https://github.com/opena2a-org/damn-vulnerable-ai-agent
- Practical DevSecOps CMCPSE launch — https://app.dealroom.co/news/feed/practical-devsecops-launches-cmcpse-first-hands-on-mcp-security-certification-at-599
- DEF CON training listings — https://training.defcon.org/products/ai-agent-security-masterclass-attacking-and-defending-autonomous-ai-systems-abhay-bhargav-vishnu-prasad-dctlv2026
- fanout.sh labs — https://fanout.sh/labs
- CSA note on OWASP LLM Top 10 2026 and the Agent Control Standard — https://labs.cloudsecurityalliance.org/research/csa-research-note-owasp-genai-top10-2026-agent-control-stand/
