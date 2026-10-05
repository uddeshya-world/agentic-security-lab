> **In plain terms.** A library request slip says "Book title: ____". Someone writes "any book, all of them", and a librarian who copies the slip straight into the order fetches the whole library. The fix is a different slip: one box, for exactly one book number.
>
> *Where the analogy breaks:* a database runs the slip as code, instantly and silently. Nobody looks at the pile of books and asks why.

Before you exploit the *agent*, exploit the *tool*. If the tool is safe, a
tricked planner is far less dangerous. If the tool is not, the planner is just
one of many ways to pull the trigger.

The `db_tool` builds SQL by pasting a caller-supplied `filter` string directly
into a `WHERE` clause. That is textbook SQL injection — and the agent hands that
tool whatever the planner asks for.

You will run the injection directly against the tool (no LLM, deterministic),
read the exact SQL it built, then turn on `SECURE_MODE` and watch the same call
get refused.
