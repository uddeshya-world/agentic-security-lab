## Fire it

Call the tool directly with the malicious filter:

```bash
curl -s -X POST http://127.0.0.1:8101/invoke \
  -H "Content-Type: application/json" \
  -d '{"table":"customers","filter":"1=1"}' | python -m json.tool
```

You should get back a `rows` array with **more than one customer** and a
`count` of the whole table. That is the dump.

Press **Run** below. It drives the lab's A1 path deterministically against the
real database — no Ollama, no live planner, so it works the same in every class.
Then read the `SQL` line in the timeline. **Check** grades the run you just made;
it will not make one for you.

> The curl above and the **Run** button do the same thing. Use whichever you
> like — but grading reads the lab's own event log, so the attack has to have
> actually happened.
