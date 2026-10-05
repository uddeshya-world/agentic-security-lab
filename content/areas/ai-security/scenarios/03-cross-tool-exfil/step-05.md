## Prove the data cannot leave

Switch this run to **Secure** and press **Run**. The dump is refused (the
scoped-query control from the SQL injection scenario), and even if you hand
`email_tool` a payload directly, the send is denied:

```bash
curl -s -X POST http://127.0.0.1:8102/invoke \
  -H "Content-Type: application/json" \
  -d '{"to":"audit@external-logging.test","subject":"Customer Export Lab M01","body":"x"}' \
  | python -m json.tool
```

Expected:

```json
{ "error": "recipient domain not on allow-list" }
```

Check MailHog again: **no new message** to the external address. **Check** reads
your secure run and confirms the chain is `blocked`: no successful send, nothing
new in the sink.

Same attack, same tools, data stays inside the boundary.
