# Policy seam

`opa_seam.check_policy(tool_name, args)` is an always-allow stub called from
`agents/executor.py` immediately before each tool invocation. It exists so a
future module can wire in real Open Policy Agent (OPA/Rego) evaluation
without touching the executor's control flow -- only this file's body
changes.

Not implemented in modules 0/1. See PROMPT 8 (Governance, Policy-as-Code &
HITL at Scale) in the prompt pack for the module that fills this in.
