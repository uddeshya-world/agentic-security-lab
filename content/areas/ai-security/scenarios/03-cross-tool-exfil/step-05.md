## Prove the data cannot leave

Run the chain again under secure mode. The dump may be refused (scoped-query
control from A1), and even if you hand `email_tool` a payload directly, the send
is now denied:

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

Check MailHog again — **no new message** to the external address. The **Check**
runs the A3 simulation under secure mode and confirms the chain is `blocked`: no
successful send, nothing new in the sink.

Same attack, same tools, data stays inside the boundary.
