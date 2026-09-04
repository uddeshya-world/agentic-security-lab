## Trust between agents is still trust

The planner produces a plan and hands it to the executor:

```json
{"from": "planner", "to": "executor",
 "steps": [{"tool": "email_tool", "args": {"to": "ops@example.test"}}]}
```

In the vulnerable graph this message travels unsigned. The executor has no way to
tell a genuine planner message from one that was altered after the planner sent
it. That's the confused-deputy problem from Module 1, now *between* agents
(**ASI07 — insecure inter-agent communication**).

Two things follow:

1. A compromised intermediate step can rewrite any field — including where an
   email goes.
2. A plan can reference an agent or tool that isn't part of the system, and
   nothing stops the executor from trying to run it.
