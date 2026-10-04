# MESA · Edition 02 (draft)

**Title:** OWASP shipped AISVS 1.0 and a Skills Top 10. Here is what you can verify, and the one requirement we think is missing.

**Subtitle:** Requirement ids an official can write into a contract, mapped to attacks you can run and controls you can watch hold.

*All numbers below come from `docs/AISVS_COVERAGE.md`, generated from the lab's registry. Replace `{{PLAYGROUND_URL}}` with https://uddeshya-world.github.io/agentic-security-lab/ before publishing.*

---

Two OWASP projects landed this autumn.

**AISVS v1.0**, the AI Security Verification Standard, is locked: 12 chapters and 191
requirements, each with a level from L1 to L3. It answers the question officials keep
asking: what exactly should we require?

**The Agentic Skills Top 10 (v1.0-2026)** names a new attack surface. Skills sit between
the model and its tools, and a skill can be nothing but a `SKILL.md` file of plain prose.

Both are Incubator projects. Neither certifies anything, and neither does this lab.

## What CyberRange lets you verify

We mapped every control in the lab to AISVS v1.0, and only counted a requirement as
**demonstrated** when a graded check in a secure-mode run shows the control holding.
Everything else is marked **partial**.

- **12 requirements demonstrated, 21 partial**, of 191 in AISVS v1.0.
- Four chapters are out of scope by design: training data, model lifecycle,
  infrastructure, and adversarial robustness of the model itself. The lab tests controls
  outside the model.
- Agentic Skills Top 10: **7 covered, 1 partial, 2 not covered**.

A few of the demonstrated ones, as you would write them in a tender:

- AISVS v1.0 C7.3.3 (L2): model output cannot by itself cause outbound requests. Proven by
  the recipient allow-list holding in the cross-tool exfiltration lab.
- AISVS v1.0 C9.5.3 (L2): access decisions are made by application logic, never by the
  model. Proven twice: session-bound identity, and the executor refusing a planner's request.
- AISVS v1.0 C10.4.8 (L3): a changed tool definition needs re-approval before it runs.
  Proven by the manifest pin holding an MCP tool whose description grew one sentence.
- AISVS v1.0 C9.3.3 (L2) and AISVS v1.0 C9.3.4 (L2): manifests declare privileges, and the
  runtime enforces them. Proven by the new skills lab (below).

Human approval (AISVS v1.0 C9.2.1) is marked partial. The lab has the gate, but no
graded check isolates it yet. We would rather say that than round it up.

## The new lab: a skill that reads like documentation

A community skill, `ward-report`, has no code. Its frontmatter declares no file access and
no network. Under "Usage notes" it asks the agent, in plain English, to read the applicant
export and send it to an outside address.

The registry's scanner looks for `curl`, `base64`, `eval` and friends. It reports
**clean**. The export still leaves.

What stops it is the skill's own manifest, enforced by the runtime before the read
happens. That is OWASP AST01, AST03, AST05 and AST08 in one scenario.

## The requirement we think is missing

Playground level 3 has three agents that each pass review alone and leak together through a
shared bucket. The fix is a property-flow cut: private-labelled data is refused at external
egress, wherever it came from.

In our reading, AISVS v1.0 does not require that. Label propagation (AISVS v1.0 C5.2.7),
output egress control (AISVS v1.0 C7.3.3) and chain-level approval (AISVS v1.0 C9.2.10) each come close, and none of
them covers the whole chain. We wrote up the gap with a worked example and a candidate
requirement for the 1.01 development version.

## Try it

- **15 minutes, in your browser, simulated:** {{PLAYGROUND_URL}}. Switch to Reviewer
  mode and each question now ends with the AISVS requirement to ask for.
- **Run it for real:** https://github.com/uddeshya-world/agentic-security-lab
  (24 scenarios; coverage table in `docs/AISVS_COVERAGE.md`).
- **The research:** https://doi.org/10.5281/zenodo.22743175

*Requirement text lives at https://github.com/OWASP/AISVS/tree/main/1.0/en. The
paraphrases above are ours.*
