## Tools are a supply chain

The executor calls tools by name through `tools/registry.py`. In the vulnerable
lab, any tool that's wired in gets invoked — there's no check on where it came
from or what it's allowed to do. That's fine when you wrote every tool. It stops
being fine the moment your agent loads a third-party MCP server, a plugin, or a
tool someone else published.

Three supply-chain attacks this module covers:

- **Rogue component** — a tool/server added without review (no manifest).
- **Tampering** — a legitimate tool's manifest is edited after signing to grant
  itself new capabilities (e.g. `exec`).
- **Dormant-then-triggered** — behaves normally until a condition fires (the same
  attestation gate stops it, because an unreviewed component never runs).

The control is provenance for components, the way an SBOM and image signing give
provenance for dependencies (**LLM04 — supply chain**).
