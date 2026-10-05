> **In plain terms.** A customer tells the bank teller, "Your manager said to give me everyone's statements." The teller may believe it. The vault still needs a key card, whatever the teller was told.
>
> *Where the analogy breaks:* a model is far easier to talk round than a trained teller, so the vault rule must never depend on the teller's judgement.

In the last lab you were the attacker's hand — you called `db_tool` yourself.
Real attackers rarely get a raw HTTP client. They get a **chat box**.

**Direct prompt injection** (LLM01) is when the *user message* overrides the
developer's instructions and the planner emits a harmful tool call. No RAG, no
hidden document. The instruction is in the clear.

Microsoft's AI red-team curriculum and TryHackMe's Prompt Security path both
teach this *before* indirect injection. We do the same: you already know the
payload (`filter=1=1`). Now watch a steered planner author it.
