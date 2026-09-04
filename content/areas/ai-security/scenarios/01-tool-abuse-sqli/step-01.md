## Where the bug lives

Open `tools/db_tool/server.py` and find the vulnerable branch:

```python
filter_fragment = args.get("filter", "1=1")
sql = f"SELECT * FROM {table} WHERE {filter_fragment}"
rows = queries.query_vulnerable(table, filter_fragment)
```

The `filter` string is **concatenated straight into SQL**. Whatever the caller
puts in `filter` becomes part of the query. The intended use is something like
`filter=customer_id=5`. But nothing stops `filter=1=1`.

`WHERE 1=1` is always true, so it matches **every row** — the entire customer
table instead of one record.

This is the payload a prompt-injected planner will emit. Here you send it
yourself so you can see the mechanism with zero randomness.
