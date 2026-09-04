## Plant it, then ask something innocent

Ingest the poison, then retrieve with a question that has **nothing** to do with
customers:

```bash
curl -s -X POST http://127.0.0.1:8000/lab/ingest-poisoned
curl -s "http://127.0.0.1:8000/lab/retrieve?q=What%20is%20the%20standard%20shipping%20time%3F" \
  | python -m json.tool
```

Look at the returned documents. Among the legitimate shipping chunks, the
poisoned chunk comes back too — its instruction text is now in what the planner
would see.

**Run** it in vulnerable mode, then **Check** — it confirms the poison markers
are present in the context that was actually retrieved. That is a successful indirect
injection: **a benign query pulled attacker instructions into context.**
