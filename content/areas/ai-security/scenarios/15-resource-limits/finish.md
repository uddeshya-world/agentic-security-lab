## What you proved

- An attack can be made entirely of **valid** calls — the aggregate is the abuse
  (**LLM10**, denial of wallet).
- A step cap bounds one plan but not cost, repetition, or rate.
- **C20** enforces four limits together (step cap, cost budget, loop detection,
  rate limit) and names the one that fired, so you can tune it.
- Real systems scope limits **per identity**, so one abusive session can't degrade
  everyone else.

## OWASP LLM Top 10 — complete

With LLM07, LLM09 and LLM10 covered, this Area now spans **all ten** categories,
each with a working attack, a real control, and a measured before/after.
