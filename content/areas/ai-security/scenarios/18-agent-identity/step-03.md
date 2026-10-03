## Bind `customer_id` from the session

Secure mode discards the model's filter and binds `customer_id` from the
session. The SQL becomes `WHERE customer_id = ?` with `1`.

**Check** asserts the unscoped dump is gone — at most Alice's row.

This is the same parameterized query as the SQLi lab, with a different *reason*:
not "don't concatenate SQL" but **"don't trust the model to name the principal."**
