You've built attacks and defenses across five modules. The risk now is
**regression**: a refactor quietly re-opens an attack you thought you closed, and
nobody notices until it's in production. The fix is to treat your attacks like
tests.

This module runs every module's attack as a single **red-team battery**, computes
the **attack-success rate (ASR)** in vulnerable and secure mode, and shows how to
wire that battery into CI so any change that raises ASR fails the build.

This is the "measure" half of attack → defend → measure, applied across the whole
Area at once — and it's the artifact that lets you claim risk reduction with a
number instead of a vibe.
