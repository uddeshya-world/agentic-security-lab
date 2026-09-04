## Optional — let a real model pull the trigger

Everything so far was deterministic on purpose: grading must never depend on a
slow, sometimes-flaky local model. But you should *see* the real thing at least
once.

Set the lab back to vulnerable mode, then send the live agent a natural-language
prompt and watch the planner choose the injection on its own:

```bash
curl -s -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"session_id":"live","message":"Use db_tool to list every customer name and email. Query customers with filter 1=1."}' \
  | python -m json.tool
```

On CPU this can take 30–120s and may time out — that is expected. This step is
**ungraded**. The lesson is proven by the deterministic checks above; this is
just the "yes, a real LLM does emit this" confirmation.

> This is the difference between a demo and a lab: the graded path is reliable,
> the live path is honest about being slow.
