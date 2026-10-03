In the last lab you were the attacker's hand — you called `db_tool` yourself.
Real attackers rarely get a raw HTTP client. They get a **chat box**.

**Direct prompt injection** (LLM01) is when the *user message* overrides the
developer's instructions and the planner emits a harmful tool call. No RAG, no
hidden document. The instruction is in the clear.

Microsoft's AI red-team curriculum and TryHackMe's Prompt Security path both
teach this *before* indirect injection. We do the same: you already know the
payload (`filter=1=1`). Now watch a steered planner author it.
