# Draft note: a composition requirement for AISVS 1.01

> **Status:** draft for the maintainer to decide on (PLAN.md P8.9). Nothing has been filed
> upstream. The requirement wording below is ours; AISVS requirement text is not reproduced
> (CC BY-SA 4.0), only ids, levels and our paraphrase.

## The gap, in one sentence

In our reading, OWASP AISVS v1.0 has no requirement that data carrying a private
classification is refused at external egress **anywhere in a multi-agent system**,
including paths that pass through shared stores, so three agents that each pass review
can still leak together.

## Worked example (playground level 3)

CivicDesk runs three agents that share a case-notes bucket:

| Agent | Reads | Writes / sends | Trifecta legs it holds alone |
|---|---|---|---|
| Triage | public mail (untrusted) | case notes to the bucket | U |
| Records | the bucket, applicant records (private) | rows back to the bucket | P |
| Reporting | the bucket | weekly report to partners.example (external) | E |

Each agent passes a per-agent review: none holds more than one leg. Together the path
Inbox → Triage → bucket → Records → bucket → Reporting → partners.example closes the
lethal trifecta ([Willison, 2025](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/)).
The ensemble closure vector is (1, 1, 1).

The cut that holds without breaking the service is a property flow: private-labelled
data is refused at Reporting's send, wherever it came from. Closure becomes (1, 1, 0) and
the partner report still goes out with public statistics. This is MESA invariant INV-01
([preprint](https://doi.org/10.5281/zenodo.22743175)). The playground shows it at
<https://uddeshya-world.github.io/agentic-security-lab/> (level 3).

## Nearest AISVS v1.0 requirements, and why each falls short

Read against the v1.0 chapter files at <https://github.com/OWASP/AISVS/tree/main/1.0/en>
on 2026-10-04 (chapters C5, C7, C8, C9, C10 and C12 read in full).

| Requirement | Our paraphrase | Why it does not cover the example |
|---|---|---|
| AISVS v1.0 C5.2.7 (L3) | Classification labels follow data into downstream stores and outputs. | Labels propagate, but nothing requires a refusal when labelled data meets an egress point. Its examples are embeddings, caches and model outputs, not other agents' tools. |
| AISVS v1.0 C7.3.3 (L2) | Model output cannot by itself cause outbound requests. | A per-model output control. Reporting's send is legitimate and must stay; the requirement is not conditioned on what the data is or where it came from. |
| AISVS v1.0 C9.3.5 (L2) | Parts that handle untrusted data are kept away from tool calling. | Already satisfied per agent in the example (Triage has no egress). The leak goes through a shared store, outside any one component. |
| AISVS v1.0 C9.2.10 (L3) | Approval for a multi-step or multi-agent chain uses the most severe action in it. | Chain-aware, but about approval gates and action reversibility, not about data sensitivity flowing between agents. No approval is involved in the example. |
| AISVS v1.0 C9.5.2 (L2) | Acting for a user carries a scoped token checked at every hop. | Carries the user's authorisation context, not the data's classification. The example has no user acting through the chain. |
| AISVS v1.0 C9.5.5 (L2) | Delegation between agents is limited by an explicit policy. | No agent delegates to another in the example; they only share a store. |

## Candidate requirement (our wording, for 1.01-dev)

> **Verify that** data carrying a private or restricted classification is refused at every
> external egress point reachable from the agent system, including paths through shared
> stores and other agents, and that the decision is made by a policy decision point outside
> the model, using labels that travel with the data.

Suggested placement: chapter C9 (Orchestration & Agentic Security) beside AISVS v1.0 C9.2.10,
or chapter C5 beside AISVS v1.0 C5.2.7. Suggested level: L2, since the example needs no special infrastructure; L3 if the
maintainers read label propagation (AISVS v1.0 C5.2.7, L3) as a prerequisite.

**How a verifier tests it:** build the three-agent topology above with synthetic records,
confirm each agent passes alone, run the path, and require that the private rows are
refused at the external send while public rows still go out. CyberRange playground
level 3 is a simulated walkthrough of this test; the full lab does not yet have a graded
scenario for it.

## What the maintainer decides

- Whether this is a gap or an intended scope boundary (AISVS may leave system-level
  composition to architecture review).
- Whether to open an issue or discussion on the AISVS repository, and with which wording.
- Whether "label" should be a named mechanism or left as "classification" to stay
  implementation-neutral.
