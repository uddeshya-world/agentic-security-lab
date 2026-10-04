## What you proved

- A skill's prose is untrusted instructions (AST01, AST05). It needs no code to leak data.
- A pattern scanner called the skill clean while it leaked (AST08).
- Enforcing the skill's declared permissions stopped the read before it happened (AST03; AISVS v1.0 C9.3.3, AISVS v1.0 C9.3.4).
- Egress allow-lists remain the backstop for the next skill that leaks through an allowed channel.

**Next:** compare with scenario 19, where the instruction hid in an MCP tool description.
