## What to ask for

- The **attack** each control is meant to stop, written as a concrete input.
- The **run record** showing where it stopped, in a mode where the control was on.
- The **same run with the control off**, showing the attack lands. Without it, you
  cannot tell a working control from an attack that never worked.
- A **regression test** that re-runs both on every change.

Controls that only lower the odds (a classifier, an instruction to the model) are
still useful. List them as such, and never count them as the stop.

In a tender, name the requirement and the evidence together, for example: "AISVS v1.0 C9.2.1 (L1),
with the run record that shows a high-impact action waiting for approval." Ask for
AISVS v1.0 C12.1.2 (L2) so the decisions are logged where you can audit them.
