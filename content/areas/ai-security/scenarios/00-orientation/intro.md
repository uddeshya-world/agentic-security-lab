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
