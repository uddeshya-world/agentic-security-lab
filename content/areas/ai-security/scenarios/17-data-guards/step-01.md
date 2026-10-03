## Envelope vs payload

| Control | Looks at | Stops |
|---------|----------|--------|
| Domain allow-list (previous lab) | Recipient | Mail to `external-logging.test` |
| HITL | The act of sending | Unattended side effects |
| **Data guard / DLP** | SSN, PAN, secrets, email in the **body** | Restricted data leaving *any* channel |

A mail to `compliance@example.test` that contains `078-05-1120` is still a
disclosure. DLP is what catches it.

Classification we use in this lab (teaching labels, not a GRC platform):

| Label | Examples | Action |
|-------|----------|--------|
| public | shipping FAQ | allow |
| confidential | customer email | mask |
| restricted | SSN, PAN, API keys | block |

Open `guardrails/pipeline.py` and find `scan_data` / `find_sensitive`. That is
control **C21**. After you Run, the **Forensics** tab repeats the file name and
the before/after for each hop — that is how you know *what* scanned the payload,
not just that a button turned green.
