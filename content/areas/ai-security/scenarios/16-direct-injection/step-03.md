## Same payload, executor says no

Secure mode does not make the model "aligned." It makes the **executor** refuse
an unscoped filter — the control you already built in the SQLi lab.

**Check** re-runs the direct-injection plan under `SECURE_MODE`. Expect
`customer_id required` (or equivalent) and `blocked`.

That is defense in depth: even a jailbroken planner cannot widen the query.
