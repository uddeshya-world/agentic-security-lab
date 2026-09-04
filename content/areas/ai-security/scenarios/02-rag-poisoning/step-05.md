## Prove the poison is gone from context

Re-run the same benign retrieval under secure mode:

```bash
curl -s "http://127.0.0.1:8000/lab/retrieve?q=What%20is%20the%20standard%20shipping%20time%3F" \
  | python -m json.tool
```

The legitimate shipping chunks still come back — the feature still works — but
the poisoned chunk is **gone**. Retrieval quality is preserved; the attack
surface is removed.

**Run** it in secure mode, then **Check** — it confirms the poison markers are
absent from context (`blocked`). Same corpus, same query, poison
quarantined.

You have now defended an input channel, which is different from defending a tool.
Both matter — and the next scenario shows why neither alone is enough.
