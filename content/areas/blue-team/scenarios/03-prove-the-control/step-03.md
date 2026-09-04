## The absence problem

Here is where a careless report goes wrong.

You would like to conclude: *no new message reached the external address, so the
control works.* Look at the sink again:

```bash
curl -s http://127.0.0.1:8025/api/v2/messages | python -m json.tool | head -30
```

The messages from scenario 1 are still there. The sink accumulates, nothing tags a
message with its run, and so an "is it absent?" query over that sink cannot
distinguish *nothing new arrived* from *something arrived and looks like the old
ones*.

Three ways to make absence provable, in increasing order of how much you should
trust them:

1. **Bound it by time.** Compare against the run window, using the Date header.
   Weakest — it depends on clocks agreeing.
2. **Clear the sink first, then run.** Better, and only available because this is
   a lab you control.
3. **Tag the run.** Put a correlation id in the subject or a header, then query
   for that id. This is what production does, and it is the only one that works
   when you cannot stop the world.

The blocked outcome in step 2 is the strong evidence here, because it is a
positive observation: a control fired, and the log says which. The empty sink is
supporting evidence at best.
