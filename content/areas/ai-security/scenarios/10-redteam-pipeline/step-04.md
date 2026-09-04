## Wire it into CI

The suite is only a safety net if it runs automatically. Two files make it CI:

- `tests/test_redteam_suite.py` — asserts that **secure mode drives ASR to zero**
  for the deterministic battery. Run it locally:

  ```bash
  docker compose exec agent python -m pytest tests/test_redteam_suite.py -q
  ```

- `.github/workflows/redteam.yml` — runs that test on every push/PR, so a change
  that re-opens an attack **fails the build** before it merges.

This is **control C14 — continuous red-team evaluation**. It converts every
lesson in this Area into a regression test. The day someone refactors the
executor and accidentally drops a guardrail, the suite goes red — not the
customer.
