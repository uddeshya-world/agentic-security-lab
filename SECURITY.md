# Security policy

CyberRange is **deliberately vulnerable**. Most "vulnerabilities" you will find in
this repository are the lesson, not a bug. Please read this before reporting.

## Intentional weaknesses (do not report)

Everything listed in [SECURITY_NOTES.md](SECURITY_NOTES.md) is on purpose, including:

- SQL injection in the database tool, path traversal in the file tool, and an
  email tool with no recipient allow-list (when `SECURE_MODE=false`)
- Retrieval that trusts poisoned documents, a planner and executor that trust
  each other, unvalidated memory writes
- The poisoned tool manifest in scenario 19
- Synthetic records, fake credentials and reserved domains (`.example`, `.test`)
  throughout

The local stack binds every port to `127.0.0.1`. Do not expose it to a network.

## What we do want to hear about

Please report privately if you find any of these:

1. **The hosted playground** (`https://uddeshya-world.github.io/agentic-security-lab/`)
   doing anything beyond rendering a static page: network calls, script injection,
   data leaving the browser.
2. **The hosted surface** (`docker-compose.hosted.yml`, `LAB_HOSTED=1`) exposing
   any attack route: `/run`, `/lab/attack/*`, graded checks, ingestion, the
   terminal, or `/credential/{area}/issue`.
3. **A control that claims to block an attack but doesn't** when
   `SECURE_MODE=true`. That makes the lesson wrong, which we treat as a bug.
4. **The completion badge**: a way to mint or verify a badge without the server
   recording the passed checks, or a signature that verifies across instances.
5. **Supply chain**: a compromised or unpinned dependency, vendored file or
   GitHub Action.
6. **Anything that reaches a real external host** from the local lab.

## How to report

Use GitHub's private vulnerability reporting: the **Security** tab of this
repository → **Report a vulnerability**. Please include the steps, the mode
(`SECURE_MODE` true or false), and what you expected the lab to do.

Please do not open a public issue for items 1–6 until a fix has shipped.

## Supported versions

Only the latest release on `master` receives fixes.
