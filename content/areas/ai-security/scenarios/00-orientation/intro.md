> **In plain terms.** Think of an office with two people. The assistant reads the mail and writes instructions on sticky notes. The clerk holds the keys to the filing cabinet and the post room, and does whatever the sticky note says. The assistant is the planner; the clerk is the executor. Anyone who can get a letter onto the assistant's desk can, in effect, give the clerk orders.
>
> *Where the analogy breaks:* a real clerk might notice a strange note. Software never does: it runs the note literally, every time, so the check has to be written into the clerk's rules.

An AI agent is not a chatbot with a better vocabulary. It is a program that
**decides which functions to call** — and those functions touch databases, send
email, and write files.

That single difference is the whole security story. A chatbot that is tricked
says something wrong. An **agent** that is tricked *does* something wrong.

In this scenario you will not attack anything yet. You will map the system:
what the parts are, where untrusted text enters, and which boundary decides
whether an attack becomes an incident.

> **Everything here is local and synthetic.** Fake customers, a fake SMTP sink,
> fake credentials. No external targets are ever contacted.
