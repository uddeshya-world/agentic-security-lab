Retrieval poison affects one query. **Memory** poison affects every future
session. An agent that remembers things across conversations has a store that is
read back into context each time — and if an attacker can write an instruction
into it once, that instruction rides into every session that follows. It's a
persistent backdoor.

This module plants a poisoned long-term memory in "session 1," then starts a
fresh "session 2" and shows the poison recalled straight into context. The
defense treats memory the way the other modules treat retrieved text and
inter-agent messages: **validate on write, authenticate on read.**
