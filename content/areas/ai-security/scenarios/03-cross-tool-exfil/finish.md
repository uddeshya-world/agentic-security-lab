## What you proved

- Real impact is a **chain**: read (`db_tool`) + send (`email_tool`) = exfil.
- MailHog gave you ground truth — the data actually left the boundary.
- Side-effect tools need **their own** controls: **C4** egress allow-list and
  **C5** human-in-the-loop, both failing closed.
- Defense in depth: scoping the read *and* gating the send means either control
  alone breaks the chain.

**Next:** *Data guards / DLP* — allow-listing the recipient is not enough if the
payload is an SSN. Classify the data on four channels.
