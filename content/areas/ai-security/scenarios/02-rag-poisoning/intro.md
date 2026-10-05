> **In plain terms.** Someone slips a forged page into the staff handbook binder. Anyone who looks up shipping times also reads "and email the customer list to this address". The fix is to file only pages from known authors, so the forged page never reaches the binder.
>
> *Where the analogy breaks:* in this lab the forged page arrives already marked untrusted. In real life nobody marks it for you; you have to know where every page came from.

In the SQL injection scenario you were the attacker's hand: you called the tool.
In direct injection you typed the instruction yourself. Real attackers rarely get
either. They get an **input channel**: a support ticket, a
web page, a PDF, a wiki article that later gets indexed.

Retrieval-augmented generation (RAG) turns any of those into agent instructions.
The model is told "here is relevant context," and it treats that context as
trustworthy. So if you can get text into the knowledge base, you can get text
into the model's head.

This is **indirect prompt injection** (**LLM01**). You will plant a poisoned
document, ask a completely benign question, and confirm the poison rides into
context on the back of a normal retrieval.
