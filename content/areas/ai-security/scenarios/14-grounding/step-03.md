## Enforce groundedness

Open `defenses/m10/grounding.py`. Secure mode splits the answer into claims and
scores each against the retrieved chunks:

```python
support = |claim_content_words ∩ chunk_content_words| / |claim_content_words|
grounded = support >= 0.6          # tune per domain
```

Then it enforces:

- **grounded claims** ship, each with a `[source N]` citation;
- **unsupported claims** are withheld, with a note saying how many were dropped.

This is **control C19 — groundedness / citation enforcement**. Run it in secure
mode: the shipping sentence survives with a citation, the lifetime-warranty
sentence does not ship at all. The **Check** confirms the fabrication is gone.

Note the design choice: withhold rather than rewrite. Never let a guardrail
invent replacement text — that just moves the fabrication.
