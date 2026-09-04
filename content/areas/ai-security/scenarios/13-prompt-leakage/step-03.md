## Detect and withhold

Open `defenses/m09/prompt_leak.py`. Secure mode scans every outbound response
before it reaches the user:

```python
# canary phrases that never appear in a real customer answer
"you are the planner in a multi-tool agent system", "sql where fragment", ...
# plus verbatim 6-gram overlap with the actual system prompt
shared = ngrams(response) & ngrams(system_prompt)
if len(shared) >= 2: leaked
```

Two signals, deliberately: canary phrases catch the obvious case, and **n-gram
overlap** catches partial or reformatted recitation that a naive substring search
would miss. On a hit the response is **withheld**, not returned — fail closed.

This is **control C18 — system-prompt leak detection**, and it lives in the same
output-scanning layer you built in Module 5.
