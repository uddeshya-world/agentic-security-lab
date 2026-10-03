## Descriptions are prompts

An MCP server or tool registry hands the planner a manifest for each tool: a name,
the arguments, and a **description** written in plain language. The planner reads
that description the same way it reads the user's question.

So the description is untrusted content. Whoever can change it can steer the plan,
without touching the prompt, the retrieval store or the user.

Attestation checks *who published* the tool and *what it may do*. It does not read
the prose. Keep that gap in mind for the next step.
