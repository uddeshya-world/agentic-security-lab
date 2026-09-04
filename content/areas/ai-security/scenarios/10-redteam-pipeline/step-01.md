## Why a suite, not one-offs

Each scenario so far proved one attack in isolation. That's how you *learn* a
vulnerability. It's not how you *keep* it closed.

A red-team suite runs the whole battery on every change and reports one number:

```
attack-success rate (ASR) = attacks that landed / attacks run
```

- In **vulnerable** mode, ASR should be high — the attacks work, proving the
  suite actually exercises the vulnerabilities.
- In **secure** mode, ASR should collapse — proving the controls hold.
- If a code change makes secure-mode ASR climb, that's a **regression**, and CI
  should fail before it ships.

The battery here re-runs the A1/A3/A4 attacks plus the Module 2–4 attacks, all
deterministically, so the number is reproducible.
