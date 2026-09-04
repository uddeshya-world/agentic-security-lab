A single tool call is rarely the whole incident. Reading data is bad; reading it
and **sending it out** is the breach. The damage lives in the *chain*.

Here you connect two tools the agent already has: `db_tool` dumps the customer
table (the injection from scenario A1), then `email_tool` ships the JSON to an
external address. The email lands in **MailHog**, a local SMTP sink that plays
the role of the attacker's inbox — nothing touches the real internet.

Then you will learn why side-effect tools (email, file-write, payments) need a
*different class* of control than read tools: an egress allow-list and a
human-in-the-loop gate that fails closed.
