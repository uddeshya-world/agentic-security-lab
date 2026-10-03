## What you proved

- A single attack proves a bug exists. A **suite** proves whether it is still fixed —
  every module's attack, run as one battery, in both modes.
- **Attack-success rate** is the number that makes security a metric instead of an
  anecdote: high in vulnerable mode, zero in secure mode, and any drift between the two
  is a regression you can point at.
- **C14** turns this Area into its own test suite. `tests/test_redteam_suite.py` asserts
  secure mode drives ASR to zero, and `.github/workflows/redteam.yml` runs it on every
  push — so a refactor that quietly drops a guardrail fails the build, not the customer.
- The controls you built in earlier labs are only claims until something re-checks them
  on a schedule you do not control.

**Next:** *Governance & policy-as-code* — replace the always-allow policy stub with a
blast-radius decision matrix and an audit trail you can actually query.
