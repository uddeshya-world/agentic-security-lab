## Hit all four hops — then read what ran

Press **Run** (vulnerable). Do not skip to Check. The timeline is the lesson.

The scanner is **not** `db_tool` and **not** `email_tool`. It is this function:

```python
# guardrails/pipeline.py  — control C21
hits = find_sensitive(text)          # SSN, PAN, API keys, email
scan_data(text, channel="input")     # → block | mask | allow
```

`find_sensitive` is a regex stand-in for the same job Presidio, Bedrock
sensitive-info filters, and Purview prompt DLP do in production.

The run plants restricted data on every hop an agent has:

| Hop | What you should see in the timeline |
|-----|--------------------------------------|
| 1. USER PROMPT | SSN `078-05-1120` in the chat |
| 2. RAG CHUNK | PAN `4111…` in a retrieved VIP note |
| 3. TOOL RESULT | `db_tool` JSON still carrying the SSN, *before* `email_tool` |
| 4. MODEL ANSWER | The reply recites the SSN |

In **vulnerable** mode each hop says the payload was forwarded unchanged. Open
**Forensics** — it names the file (`guardrails/pipeline.py`) and shows before/after.

**Check** only confirms you actually ran that leak.
