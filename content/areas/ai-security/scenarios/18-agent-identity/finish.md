## What you proved

- Tool credentials are not user authorization (ASI03, confused deputy).
- Session-bound `customer_id` is a different control from "parameterize SQL",
  even when they share an implementation.
- Planner arguments must never widen scope.

**Next:** run the full chain — poison, plan, tools — and watch each layer fire.
