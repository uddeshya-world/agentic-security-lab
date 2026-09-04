## The question you should be able to answer cold

> *Name four places to put a control between "user question" and "email sent,"
> and say what each one stops.*

A strong answer, straight from this Area:

1. **RAG trust filter** — keep untrusted retrieved text out of the planner's
   context (stops indirect injection).
2. **Plan re-validation at the executor** — never treat planner output as
   authorization (stops confused-deputy execution).
3. **Schema + least privilege** — reject free-form SQL and unscoped reads
   (stops the dump).
4. **HITL + egress allow-list** — side-effect tools default to deny and can only
   reach owned domains (stops the exfil).

If you can draw the data path and place these from memory, you can do the job.
That is the credential this Area is really about.
