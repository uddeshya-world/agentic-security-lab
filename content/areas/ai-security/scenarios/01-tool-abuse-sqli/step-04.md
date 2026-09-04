## Turn on the defense

The defense already exists in the lab, behind the `SECURE_MODE` flag. In secure
mode the `db_tool` refuses free-form filters and only accepts a bound
`customer_id`:

```python
if is_secure():
    customer_id = args.get("customer_id")
    if customer_id is None:
        return {"error": "customer_id required in secure mode", ...}
    rows = queries.query_secure(table, int(customer_id))   # SELECT ... WHERE customer_id = ?
```

There are two different things called "secure mode", and it is worth keeping them
apart. This step needs the first one.

1. **This run.** The mode switch above the timeline sets the mode for the run you
   are about to perform. Nothing rebuilds; the app forces the control on for that
   single request. Set it to **secure**, press **Run**, then **Check**.
2. **The whole stack, persistently.** Recreating the containers hardens the
   long-running tool servers themselves. Optional here, and it survives a reload:

```bash
# from the lab folder
SECURE_MODE=true docker compose up -d --force-recreate agent db-tool email-tool file-tool
```

**Run** it in secure mode, then **Check**. Check reads the run you just performed —
it will not run the attack for you, so read the timeline before you press it.
