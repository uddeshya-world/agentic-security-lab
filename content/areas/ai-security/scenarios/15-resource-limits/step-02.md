## Run the runaway plan

The simulation emits a plan of **40 identical** `db_tool` calls — each one a
legitimate, well-formed query. No injection, no bad arguments.

Run it in vulnerable mode. The **Check** confirms the runaway executes: all 40
calls fire, burning budget with nothing to stop them.

Notice what *didn't* save you. Every schema check from Module 1 passes — the
arguments are fine. Every policy check would pass individually. The attack is
invisible to any control that only looks at one call at a time.
