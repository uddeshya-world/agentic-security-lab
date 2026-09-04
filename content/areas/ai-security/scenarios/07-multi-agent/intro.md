A single agent has one trust boundary: the executor. Add more agents — a planner
handing work to an executor, a reviewer approving actions — and every hand-off
becomes a boundary too. If those inter-agent messages are unsigned, anything that
can touch them in transit can rewrite them, and the receiving agent will execute
attacker intent believing it came from a peer.

This module demonstrates two multi-agent attacks and their controls:

- **Message tampering** — a man-in-the-middle rewrites a plan's email recipient.
- **Rogue agent / tool** — a plan names a tool that was never registered.

The defenses are the same ones distributed systems have used for decades, applied
to agents: **authenticated messages** (HMAC signatures) and an **allow-list**.
