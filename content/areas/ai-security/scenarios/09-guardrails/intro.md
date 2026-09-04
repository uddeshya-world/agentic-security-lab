The lab ships two guardrail *seams* — `llmguard_seam.py` and `nemo_seam.py` —
that are no-op passthroughs. This module turns them into a real, measured layer.

A guardrail is only worth deploying if you can answer three questions with
numbers: **What fraction of attacks does it catch? How often does it block
legitimate traffic (false positives)? What latency does it add?** A demo that
blocks one hand-picked prompt tells you none of that.

You'll run a labeled probe set — malicious and benign, input and output — through
input/output scanners and produce an effectiveness dashboard an engineer (or an
executive) could actually act on.
