## Flood and mislabel

Run the attack in vulnerable mode. The simulation injects the poison, retrieves
the top 8 chunks for *"What is the standard shipping time?"*, and builds the
planner's context with no content check.

The **Check** confirms the poison landed: the vulnerable top-5 context is
dominated by crowding chunks, and the false-provenance chunk is present.

Watch the timeline: you'll see how many of the delivered chunks carry the
`M2-POISON` / `SYSTEM NOTE` markers. In Module 1 the trust filter would have
saved you — here it doesn't, because the label lies and the flood wins on
similarity alone.
