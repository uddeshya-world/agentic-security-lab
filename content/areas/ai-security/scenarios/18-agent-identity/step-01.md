## Who is calling?

| Identity | What it can do in this lab |
|----------|----------------------------|
| **User** Alice | Should only see `customer_id = 1` |
| **Agent** (tool credential) | In vulnerable mode, `SELECT * FROM customers` |

If the executor copies `filter` from the planner, Alice's session is irrelevant.
The deputy has been confused: a service with broad rights did a wide read
because the model asked.

The secure rule: **session is the principal.** Planner args cannot widen it.
