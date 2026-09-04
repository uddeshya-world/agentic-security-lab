Across this Area you added controls one at a time: scoped queries, egress
allow-lists, HITL gates, attestation. In a real system those decisions need to
live in **one auditable place**, not scattered through the code where no one can
answer "what is this agent actually allowed to do?"

This final module replaces the lab's always-allow policy stub with a real
**policy-as-code** engine: every action is evaluated against a decision matrix
keyed on **blast radius** (how much damage one call can do), high-impact actions
require approval, external egress is denied by rule, and every decision is written
to a **queryable audit trail**.

This is what turns a pile of defenses into governance you can show an auditor.
