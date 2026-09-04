## What you proved

- Real impact is a **chain**: read (`db_tool`) + send (`email_tool`) = exfil.
- MailHog gave you ground truth — the data actually left the boundary.
- Side-effect tools need **their own** controls: **C4** egress allow-list and
  **C5** human-in-the-loop, both failing closed.
- Defense in depth: scoping the read *and* gating the send means either control
  alone breaks the chain.

**Next:** *Exploit the agent* — the capstone. Poison enters via RAG, the planner
emits this exact chain on its own, and the executor decides whether it runs.
