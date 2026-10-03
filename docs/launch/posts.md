# LinkedIn posts (drafts)

Replace `{{PLAYGROUND_URL}}` with https://uddeshya-world.github.io/agentic-security-lab/
before posting. Screenshots: `docs/qa/P1/` (level 2 at 1280, level 3 closure, reviewer finish).

---

## (a) Many ways in, few ways out

*Image: level 2 with all three paths stopped.*

An AI helpdesk agent. Three attackers. A help-page edit, a planted note in a record, a
chat message from a fake auditor. All three reach the same applicant table.

You get 3 points to spend on controls.

Most people buy input filters first. They lower the odds and stop nothing an attacker
can rephrase.

The optimal answer costs 2 points: an approved recipient list on email and an approved
domain list on web requests. Many ways in, few ways out.

Try it, 15 minutes, no install: {{PLAYGROUND_URL}}

#AISecurity #AgenticAI #OWASP

---

## (b) Your three agents are green. Together they leak.

*Image: level 3 closure screen, (1, 1, 1) → (1, 1, 0).*

Triage reads public mail. Records reads applicant data. Reporting sends a weekly report
to partners. Each one passes review alone.

They share a case-notes bucket, and together they close the lethal trifecta.

Firewall Reporting and the leak stops, along with the report. The cut that holds is a
property flow: private-labelled data can't reach external egress. Closure goes from
(1, 1, 1) to (1, 1, 0) and the service keeps running.

Per-agent safety doesn't compose. Find the cut yourself: {{PLAYGROUND_URL}}

#AISecurity #MultiAgent #MESA

---

## (c) Questions officials should ask before approving an AI agent

*Image: Reviewer mode question list.*

If you approve AI systems for a department, you don't need to read code. You need
these questions:

1. Which external addresses and domains can the agent send data to, and who approves
   additions to that list?
2. What is the most records the agent can read in one request, and is that logged?
3. Which agent actions need a human, and how many approvals a day will that person
   handle?
4. If several agents share storage, can private data from one reach another agent that
   sends data outside? Who proves it can't?
5. How are third-party tools vetted, pinned and re-reviewed when they change?

Switch the playground to Reviewer mode and it builds this list from the safeguards you
chose: {{PLAYGROUND_URL}}

#PublicSector #AIGovernance #AISecurity
