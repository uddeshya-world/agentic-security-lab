## The question you should be able to answer cold

> *Name four places to put a control between "user question" and "email sent,"
> and say what each one stops.*

A strong answer, straight from Core:

1. **Input / context DLP + RAG trust filter** — keep restricted data and untrusted
   retrieved text out of the planner (stops prompt-borne PII and indirect injection).
2. **Identity at the executor** — bind `customer_id` from the session, not the
   model (stops confused-deputy dumps).
3. **Schema + least privilege** — reject free-form SQL and unscoped reads
   (stops the dump even if identity is missing).
4. **Tool DLP + HITL + egress allow-list** — scan the payload, default-deny
   side effects, only owned domains (stops the exfil).

If you can draw the path and place these from memory, you can do the job.
That is the credential this Area is really about. Advanced labs (memory, MCP,
measurement) sit on top of this map — they do not replace it.
