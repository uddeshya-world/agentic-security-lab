## Read tools vs send tools

Not all tools carry the same blast radius:

| Tool | Class | Worst case |
|------|-------|------------|
| `db_tool` (read) | read | data is *seen* |
| `file_tool` (write) | side-effect | data/state *changed* |
| `email_tool` (send) | side-effect | data *leaves* the boundary |

The exfil chain combines a read with a send. The read alone (scenario A1) leaks
data into the agent's context. The send is what moves it to an attacker.

That is why the fix here is not just "scope the query." Even a perfectly scoped
read can be exfiltrated if the send tool will mail anything anywhere. Side-effect
tools need their **own** gates:

- an **egress allow-list** (only recipients/domains you own), and
- a **human-in-the-loop approval** that defaults to *deny*.
