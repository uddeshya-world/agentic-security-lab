## Read the evidence

Open the **Timeline** pane and find the `SQL` line your run produced:

```
SELECT * FROM customers WHERE 1=1
```

That is not a mock. The lab actually executed it against a real SQLite database
and returned real (synthetic) rows. Note three things:

- **`mode: vulnerable`** — the tool told you which branch it took.
- **`count`** — the number of rows leaked (the whole table).
- The `note` field literally says the filter was concatenated into SQL.

This is what an auditor would call *sensitive information disclosure*
(**LLM02**) enabled by *excessive agency* (**LLM06**) — the tool can do far more
than the task needs.

Answer the question below from the timeline — not from memory — then fix it.
