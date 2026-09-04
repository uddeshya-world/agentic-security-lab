## Prove it gates and logs

Run the same sequence in secure mode. The DB read (medium blast) auto-allows; the
file write (high) requires approval; the internal email (critical) requires
approval; the external email is **denied by rule**. Every decision lands in the
audit trail.

The **Check** confirms both halves: the external-egress action is blocked, and the
audit trail is complete (every evaluated action logged). Open **Forensics** to see
the audit sample — who/what/decision/why/when.

That completes the arc: you can now not only stop each attack, but express *why*
an action is allowed or denied as reviewable policy, and prove after the fact
exactly what the agent did.
