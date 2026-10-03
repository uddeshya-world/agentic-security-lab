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
