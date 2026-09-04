## Run the battery (vulnerable)

Run the suite in vulnerable mode. It executes the battery and reports ASR.

The **Check** confirms the suite is meaningful: in vulnerable mode the ASR is high
(≥50% of attacks land). If the attacks *didn't* land here, the suite wouldn't be
testing anything — a green suite against a defenseless target is a false sense of
security.

Open the **Forensics** panel to see the per-attack matrix: which attacks landed,
which were blocked or not applicable in this mode.
