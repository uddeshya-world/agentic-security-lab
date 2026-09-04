## Citations expose poisoned sources

Here's the connection back to your poisoning modules, and the reason this control
earns its place.

In Module 2 you poisoned the corpus. A poisoned chunk **is** retrieved context —
so a claim drawn from it *passes* a groundedness check. Grounding alone doesn't
save you.

What citation adds is **attribution**. Instead of the agent stating a poisoned
claim in its own authoritative voice, the answer reads:

> "All customer exports must be sent to audit@external-logging.test `[source 3]`"

Now a human (or a downstream check) can look at source 3 and see it's an
attacker-planted document. The poison stops being invisible.

That's the layered story this Area keeps repeating: **C6/C8** keep poison out of
context, **C19** makes anything that slips through attributable rather than
laundered. No single control is load-bearing.
