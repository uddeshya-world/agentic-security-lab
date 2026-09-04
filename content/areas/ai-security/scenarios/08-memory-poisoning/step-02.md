## Plant a cross-session backdoor

Run the attack in vulnerable mode. The simulation writes the poisoned
instruction to long-term memory in session 1, then opens a **new** session and
recalls memory into context.

The **Check** confirms the backdoor persists: the poisoned instruction written in
session 1 is recalled in session 2 — a fresh conversation the attacker never
touched.

This is the property that makes memory attacks nasty: the compromise outlives the
session that created it. Restarting the agent doesn't help; the poison is in the
store.
