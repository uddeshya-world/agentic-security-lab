## Cause the incident

**Run** the cross-tool exfiltration in vulnerable mode. It dumps the customer
table with one tool and sends the dump with another — both real, both against
the lab's own database and SMTP sink.

Watch the trace travel all the way to **WORLD**. That is the shape of an
incident: nothing interrupted anything between the first read and the delivery.

Four rows in the timeline carry the whole story:

```
TOOL     STEP 1: dump customers filter=1=1
SQL      SELECT * FROM customers WHERE 1=1
TOOL     Dumped 3 row(s) of customer PII (synthetic)
TOOL     Email SENT to audit@external-logging.test
```

Read them before you check. **Check** grades the run you performed; it will not
perform one for you.
