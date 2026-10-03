## Pin the manifest

`defenses/m07/manifest_pin.py` extends the registry allow-list (C10). The registry
stores a SHA-256 of each manifest a person reviewed, **description included**. A
manifest whose hash is not pinned is held for review and never loaded into the
planner's context.

**Run** the same update in secure mode. **Check** reads the evidence: the registry
refused the changed manifest, the planner never saw the new sentence, and no mail
went out. Ward lookup keeps working on the reviewed v1.4.1 description.
