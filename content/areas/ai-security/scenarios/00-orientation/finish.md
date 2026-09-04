## You can now explain the attack surface

- The agent data path: **user → RAG → planner → executor → tools**.
- Untrusted text enters at RAG, user input, and memory.
- The **executor** is the trust boundary — the last chance to refuse a harmful
  plan before it hits real tools.
- A permissive **tool schema** is the door every later attack walks through.

Nothing was attacked yet. That changes now.

**Next scenario:** *Tool abuse — SQL injection*, where you dump an entire
customer table through the agent's own database tool.
