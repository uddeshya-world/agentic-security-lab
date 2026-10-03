## What you proved

- Direct prompt injection is LLM01 through the **user** channel.
- A steered planner will emit the same `filter=1=1` you typed by hand.
- The fix is still outside the model: schema + least privilege at the executor.

**Next:** plant that instruction in a document and let retrieval carry it —
indirect injection.
