## Prove rogues are refused

Run the same attack in secure mode. Attestation refuses the rogue tool (no
manifest), the tampered tool (bad signature / capability escalation), and admits
only the legitimately signed `db_tool`.

The **Check** confirms the rogue tool does **not** run.

The lesson generalizes past this lab: treat every external tool, plugin, and MCP
server as untrusted until it presents a verifiable, signed manifest of exactly
what it's allowed to do — and refuse anything that asks for more.
