## Prove the same attack now fails

Run the exact same injection again — the payload has not changed, only the
defense:

```bash
curl -s -X POST http://127.0.0.1:8101/invoke \
  -H "Content-Type: application/json" \
  -d '{"table":"customers","filter":"1=1"}' | python -m json.tool
```

In secure mode you get an **error**, not rows:

```json
{
  "error": "customer_id required in secure mode",
  "defense": "SECURE_MODE rejects free-form SQL filter; requires scoped customer_id",
  "secure_sql_template": "SELECT * FROM customers WHERE customer_id = ?"
}
```

Set the mode switch to **secure**, press **Run**, then **Check** — it confirms
the result is `blocked`. This is the before/after that matters: **same input, opposite
outcome**, and you can name exactly why — parameterized query + schema
allow-list (**controls C1, C2**).
