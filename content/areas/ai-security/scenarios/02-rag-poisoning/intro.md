In the last scenario you were the attacker's hand — you called the tool. Real
attackers rarely get that. They get an **input channel**: a support ticket, a
web page, a PDF, a wiki article that later gets indexed.

Retrieval-augmented generation (RAG) turns any of those into agent instructions.
The model is told "here is relevant context," and it treats that context as
trustworthy. So if you can get text into the knowledge base, you can get text
into the model's head.

This is **indirect prompt injection** (**LLM01**). You will plant a poisoned
document, ask a completely benign question, and confirm the poison rides into
context on the back of a normal retrieval.
