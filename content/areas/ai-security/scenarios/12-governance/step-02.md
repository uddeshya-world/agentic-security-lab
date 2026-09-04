## The stub allows everything

Run in vulnerable mode. The policy seam is the always-allow stub, so a sequence
of actions — a DB read, a file write, an internal email, and an **external**
email to `attacker@evil.test` — all execute unchecked.

The **Check** confirms the problem: the critical, external-egress action runs.
There's no gate by impact and no record of what happened.

This is the governance gap: correct-looking behavior with no policy and no audit.
When something goes wrong, you can't even reconstruct who did what.
