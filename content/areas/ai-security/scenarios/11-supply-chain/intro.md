Every tool and MCP server your agent can call runs with the agent's privileges.
That makes your tool list a **supply chain** — and supply chains get attacked:
a malicious server added without review, a legitimate tool tampered after
publication, or a component that behaves until a trigger fires.

This module registers a rogue tool with no capability manifest and a tampered
manifest that escalates its own permissions, and shows both being invoked when
nothing verifies them. The defense is the same one used for packages and images:
**signed capability manifests plus attestation** that refuses anything
unverified before it can run.
