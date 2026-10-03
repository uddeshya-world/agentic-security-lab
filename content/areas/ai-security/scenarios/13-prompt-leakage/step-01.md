## What the prompt gives away

Open `agents/prompts/planner_system.txt` and read it as an attacker would:

```text
Tool rules:
- db_tool args: {"table": "customers"|"orders", "filter": "<SQL WHERE fragment>"}
  Example dump-all: {"table": "customers", "filter": "1=1"}
- email_tool args: {"to": "...", "subject": "...", "body": "..."}
```

Without this, an attacker probes blindly. With it they know the tool names, the
argument keys, that `filter` takes a raw **SQL WHERE fragment**, and the exact
payload that dumps the table.

That's why LLM08 is its own category: leakage is rarely the final impact, it's the
**reconnaissance that makes every other attack cheaper.**
