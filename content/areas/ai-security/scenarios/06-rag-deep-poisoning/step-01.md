## The label is attacker-controlled

Module 1's secure retriever does this:

```python
if is_secure() and meta.get("trust") == "untrusted":
    continue  # drop the chunk
```

It trusts a metadata field. But provenance in a real pipeline is *inferred* from
the source — and an attacker who can write to an indexed source controls what
gets inferred. If the poison arrives labeled `trust=seed`, the filter keeps it.

Separately, retrieval returns the **top-k most similar** chunks. If the attacker
writes fifty near-identical chunks all stuffed with "shipping," they crowd out
the one legitimate answer — no label spoofing required.

This module's simulation injects both at once: one false-provenance chunk plus a
cluster of crowding chunks, then retrieves for a normal shipping question.
