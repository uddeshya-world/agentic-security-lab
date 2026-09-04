## What you proved

- An agent's tools/MCP servers are a **supply chain** — an unverified component
  runs with the agent's privileges (**LLM03**).
- **C15** (signed capability manifests + startup attestation) refuses rogue,
  tampered, unknown, or over-scoped components, failing closed.
- The same provenance discipline as SBOMs and image signing, applied to tools.

**Next:** *Governance & policy-as-code* — make "who may do what" an auditable rule,
not a scattering of if-statements.
