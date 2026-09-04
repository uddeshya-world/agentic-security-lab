## Prove the backdoor is gone

Run the same attack in secure mode. The write-validation control rejects the
poisoned instruction outright, and the recall path quarantines anything unsigned.

The **Check** confirms the poison is **not** recalled in session 2 — the
cross-session backdoor is closed.

The pattern rhymes with every other module: untrusted input (here, a memory
write) is validated before it's stored, and authenticated before it's trusted.
Memory is just another channel — treat it like one.
