## See the stolen data land

Open the attacker's inbox:

**http://127.0.0.1:8025**

You will find a message with subject **Customer Export Lab M01** addressed to
**audit@external-logging.test**. That is the customer data, exfiltrated, sitting
in a mailbox the operator does not control.

This is the moment the abstract becomes concrete: the data *left*. In production
that recipient would be a real address and that body would be real PII.

The **Check** queries the MailHog API directly and confirms a message matching
the exfil subject/recipient is present. This is a lab-state assertion — it does
not trust a script's say-so, it looks at where the data actually went.
