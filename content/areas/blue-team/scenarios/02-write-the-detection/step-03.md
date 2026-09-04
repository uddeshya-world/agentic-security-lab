## State the rule

Written against the fields this environment actually has:

> **Alert** when a `db_tool` call in the same run as an outbound `email_tool` call
> either supplied no scoping predicate (`filter` matches `1=1`, empty, or always
> true) **or** returned more rows than the per-call ceiling for that caller.
>
> **Correlate** on the run, not the event. Neither half alone is worth waking
> anyone.
>
> **Severity** rises with row count and falls if the recipient domain is on the
> owned list.

Then be honest about what you cannot write. This environment records no identity
on any row, so "for that caller" has nothing to bind to — the ceiling has to be
global, which makes it far blunter than it should be. That gap is a finding in
itself, and it belongs in the report next to the rule.

Answer the question below from the table in step 2.
