## Corroborate it in the sink

The event log says the email tool *reported* sending. That is the tool's own
account of itself. A second source makes it a finding:

```bash
curl -s http://127.0.0.1:8025/api/v2/messages | python -m json.tool | head -40
```

Or open `http://127.0.0.1:8025` and read the body. It is the customer table.

**You will probably see several near-identical messages.** The sink accumulates
across every run on this machine, and nothing tags a message with the run that
produced it. So correlate on the **Date header**, not the subject: your incident
is the message whose timestamp falls inside the window of the run you just
performed.

That is not a lab quirk. Shared sinks without correlation ids are exactly how
real triage goes wrong — an analyst reads an old artefact and reports an ongoing
breach that actually stopped a week ago.
