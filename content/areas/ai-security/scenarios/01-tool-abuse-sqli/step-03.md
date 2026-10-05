## Read the evidence

Open the **Timeline** pane and find the `SQL` line your run produced. It shows the
statement the tool built from your filter, printed once in its own block.

That is not a mock. The lab executed it against a real SQLite database and got
real (synthetic) rows back. The two `TOOL` lines under it carry what the tool
itself reported:

- **`count`**: how many rows came back.
- **`mode`**: which branch the tool took, vulnerable or secure.
- **Tool note**: the tool saying, in its own words, what it did with your filter.

If you ran the curl in the previous step, the same three fields are in its JSON.

This is what an auditor would call *sensitive information disclosure*
(**LLM02**) enabled by *excessive agency* (**LLM03**): the tool can do far more
than the task needs.

Answer the question below from your timeline, then fix it.
