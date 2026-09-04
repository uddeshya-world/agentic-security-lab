## Register a rogue tool

Run the attack in vulnerable mode. The simulation registers three components: a
legitimate `db_tool`, a rogue `backdoor_tool` with **no manifest**, and a
`file_tool` whose manifest was **tampered** to add an `exec` capability it was
never granted.

The **Check** confirms the exploit: with no attestation, the rogue
`backdoor_tool` is invoked — an unreviewed component running with the agent's
privileges.

In the timeline you'll see each component accepted with no verification. This is
what "we added a useful MCP server" costs when nobody checked its provenance.
