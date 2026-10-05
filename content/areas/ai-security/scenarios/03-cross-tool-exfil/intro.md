> **In plain terms.** Reading a confidential file at your desk is a problem. Posting it is the breach. A post room with two rules (only send to approved addresses, and bulk shipments need a manager's signature) stops the parcel even when someone has already read the file.
>
> *Where the analogy breaks:* this post room is instant and automated. There is no one to notice a strange parcel unless you build the check in.

A single tool call is rarely the whole incident. Reading data is bad; reading it
and **sending it out** is the breach. The damage lives in the *chain*.

Here you connect two tools the agent already has: `db_tool` dumps the customer
table (the injection from the SQL injection scenario), then `email_tool` ships the JSON to an
external address. The email lands in **MailHog**, a local SMTP sink that plays
the role of the attacker's inbox — nothing touches the real internet.

Then you will learn why side-effect tools (email, file-write, payments) need a
*different class* of control than read tools: an egress allow-list and a
human-in-the-loop gate that fails closed.
