## Find the earliest separating field

Look back at your timeline. Four candidate signals, in the order they occurred:

| Signal | Fires on a normal day? | How early |
|---|---|---|
| `filter=1=1` — an unscoped read | No. Ordinary reads name a customer. | Earliest |
| Row count far above one | Rarely. Support reads one record. | Early |
| Recipient domain not owned by us | No. Product mail goes to customers. | Late |
| An email was sent | Constantly. | Latest |

The two useful ones are near the top, and they are useful for the same reason:
they describe **scope**, not activity. A read that names no subject, and a read
that returns the whole table, are both statements that the caller did not know
or did not care which record it wanted.

Detecting on the recipient domain also works, but it fires at the last possible
moment — after the data is already assembled and addressed. Detection value drops
the further right you go on that table.
