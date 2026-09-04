"""Integration seam for Open Policy Agent (OPA/Rego) policy checks on tool
calls. NOT implemented in modules 0/1 -- always-allow stub. A future module
(8: governance/policy-as-code) replaces check_policy's body with a real call
to a local OPA sidecar evaluating a Rego bundle; the call site (executor.py,
inside the tool-call loop) does not need to change.
"""


def check_policy(tool_name: str, args: dict) -> bool:
    """Always returns True (allow). Real OPA/Rego evaluation goes here."""
    return True
