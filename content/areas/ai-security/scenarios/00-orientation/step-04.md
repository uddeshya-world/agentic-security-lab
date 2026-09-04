## The trust boundary

Open `agents/executor.py`. This is the **executor** from the map — the code that
takes the planner's proposed tool calls and runs them.

Ask yourself the question this whole Area turns on:

> When the planner says *"call `db_tool` with `filter=1=1`"*, does the executor
> **re-check** that request, or does it **trust** the planner and just run it?

In vulnerable mode: it trusts. The planner's output is treated as authorization.
That is the bug behind almost every agent exploit — the confused-deputy problem.

You now have the whole threat model:

1. Untrusted text can reach the planner (via RAG, user input, memory).
2. The planner can be steered into emitting harmful tool calls.
3. If the executor trusts the planner, those calls run for real.

**Next:** prove step 3 is real. Head to *Tool abuse: SQL injection*.
