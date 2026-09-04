## What you proved

- Every agent-to-agent hand-off is a trust boundary. Unsigned messages are
  unauthenticated instructions (**ASI07**).
- **C9** (HMAC-signed messages, verified before acting) makes tampering
  detectable; **C10** (registry allow-list) blocks rogue agents/tools.
- More agents can mean more capability without more risk — but only if the
  channels between them are authenticated.

**Next:** *Memory poisoning* — attacks that persist across sessions by planting
instructions in long-term memory.
