## What you proved

- A leaked system prompt is **reconnaissance**: in this lab it hands over every
  tool name, argument shape, and a working dump-all payload (**LLM07**).
- **C18** detects disclosure on the output path using canary phrases plus n-gram
  overlap, and withholds the response — failing closed.
- Detection is damage control. The durable posture: treat the prompt as public,
  keep secrets and enforceable policy out of it, and make the system safe even
  when the attacker has read it.

**Next:** *Groundedness & citations* — stopping the agent from stating things no
source supports.
