Every attack so far had a malicious *shape* — bad SQL, a poisoned document, a
tampered message. This one doesn't. Each individual call is perfectly ordinary.
The attack is the **aggregate**.

An agent stuck in a loop, or steered into a 40-step plan of legitimate queries,
burns tokens, API spend, and rate limits until the bill arrives or the service
degrades. That's **denial of wallet** — and it's why LLM06 exists as its own
category.

This lab already caps plan length, which is exactly why LLM06 was only *partially*
covered. You'll see why a step cap alone is insufficient, then build the other
three limits alongside it.
