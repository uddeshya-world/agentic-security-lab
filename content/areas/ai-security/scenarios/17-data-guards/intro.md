> **In plain terms.** Airport security has two checks. The boarding pass says where you may go; the X-ray says what is in your bag. A valid ticket does not carry a prohibited item through. The recipient allow-list is the boarding pass; DLP is the X-ray.
>
> *Where the analogy breaks:* the lab's X-ray is a set of patterns for SSNs and card numbers. Real data in unusual formats can slip past pattern matching.

You already caused an incident: three synthetic customers left through email.
The control you turned on was an **egress allow-list** — only `@example.test`.
That stops `audit@external-logging.test`. It does **not** stop mailing the whole
customer table to a colleague.

Production AI platforms treat this as a separate product: Bedrock *sensitive
information filters*, Microsoft Purview DLP on prompts, NVIDIA NeMo PII rails,
Azure Content Safety redaction. They all sit at the same place in the pipeline:
the input and output boundary, before the data reaches anything that can move it.

**Data guards** classify what moved and then **block or mask** it, on every hop
an agent has — not just the chat bubble.
