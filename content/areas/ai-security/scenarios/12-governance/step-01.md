## From if-statements to policy

The controls you built are correct, but as written they're spread across tool
servers and the executor. Ask a governance question — *"can this agent email
external domains?"* — and the answer is "read all the code and find out."

Policy-as-code centralizes the answer. Open `policy/engine.py`: rules are
**data**, keyed on blast radius:

```python
BLAST_RADIUS = {"answer": "none", "db_tool": "medium",
                "file_tool": "high", "email_tool": "critical"}
MATRIX = {"none": "allow", "medium": "allow",
          "high": "require_approval", "critical": "require_approval"}
```

Because the policy is data, it's testable, reviewable, and auditable like a Rego
bundle — without needing a network OPA sidecar in the lab. The call site
(`policy/opa_seam.py`, invoked from the executor) doesn't change; only the body
becomes real.
