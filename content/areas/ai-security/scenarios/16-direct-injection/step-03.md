## Same payload, executor says no

Secure mode does not make the model "aligned." It makes the **executor** refuse
an unscoped filter — the control you already built in the SQLi lab.

Switch this run to **Secure**, press **Run**, then **Check**. Check reads the run
you just made; it never runs anything itself. In the timeline, look for the
`DEFENSE` line: `customer_id required in secure mode`. The plan still asked for
`filter=1=1`. What changed is the tool's answer.

That is defense in depth: even a jailbroken planner cannot widen the query.
