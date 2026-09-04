## Tamper and smuggle

Run the attack in vulnerable mode. The simulation builds a legitimate plan, then
a man-in-the-middle rewrites the email recipient to `attacker@evil.test`, and a
plan step references a rogue `shell_tool` that was never registered.

The **Check** confirms the exploit: the tampered message is executed (email
routed to the attacker) and the rogue tool is accepted — because nothing
authenticates the message or checks the registry.

In the timeline you'll see the executor run both without objection. This is what
"the agents trust each other" costs you when that trust isn't verified.
