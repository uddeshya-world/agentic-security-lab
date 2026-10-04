## Enforce the manifest

Control **C22** makes the runtime enforce what the skill declares. `ward-report`
declares `files: []`, so the read of `workspace/exports/applicants.csv` is refused
**before it happens**, whatever the prose says.

**Run** in secure mode. **Check** reads the evidence: the skill manifest refused the
read, the file was never opened, and no mail went out.

The file tool's workspace jail allows this path, so the jail is not what stops it here.
The egress allow-list on `send_email` would refuse `ward-data.example` too, but the run
never reaches it. That is the backstop, not the control.

This is the pair AISVS v1.0 C9.3.3 (L2) and AISVS v1.0 C9.3.4 (L2) ask you to verify:
manifests declare privileges, and the runtime enforces them.
