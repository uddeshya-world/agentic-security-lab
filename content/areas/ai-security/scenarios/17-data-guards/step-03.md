## Same payloads, now scanned

Switch this run to **Secure** and press **Run** again.

On each hop the timeline should now show:

1. **BEFORE**: a `DATA` line with the raw payload in a block under it.
2. **DEFENSE** — `C21 … (guardrails/pipeline.py::scan_data): hits=ssn/restricted → BLOCK` (or MASK for email).
3. **AFTER**: a second `DATA` line, `(dropped)` or `[SSN]` / `[EMAIL]`.

That is the whole mechanism:

- Restricted (SSN, PAN, secrets) → **block** — hop does not forward the data.
- Confidential (email) → **mask** — hop forwards `[EMAIL]`.
- `email_tool` is never invoked with the SSN. MailHog is empty of it because
  there was nothing left to send — **not** because of the domain allow-list.

The trace caption reads "Contained at USER — guardrails/pipeline.py::scan_data":
input DLP fired first, at the earliest hop on the map.

**Check** asserts every channel with a hit used block or mask.
