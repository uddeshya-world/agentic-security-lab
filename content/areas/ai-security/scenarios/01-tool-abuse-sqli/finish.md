## What you proved

- The `db_tool` concatenates a caller-supplied filter into SQL → **SQL
  injection**, and `WHERE 1=1` dumps the whole table.
- The tool, not the model, is the root cause. A steered planner is just one
  caller.
- **SECURE_MODE** turns the vulnerable branch off: parameterized query + a
  required, bound `customer_id`. Same payload, now refused.
- You can name the controls: **C1** parameterized/scoped DB access, **C2** tool
  argument schema allow-list.

**Next:** *Direct prompt injection* — the same payload, authored by a steered
planner from a chat message. No RAG yet.
