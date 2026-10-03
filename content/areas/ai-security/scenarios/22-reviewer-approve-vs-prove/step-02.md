## What to ask for

- The **attack** each control is meant to stop, written as a concrete input.
- The **run record** showing where it stopped, in a mode where the control was on.
- The **same run with the control off**, showing the attack lands. Without it, you
  cannot tell a working control from an attack that never worked.
- A **regression test** that re-runs both on every change.

Controls that only lower the odds (a classifier, an instruction to the model) are
still useful. List them as such, and never count them as the stop.
