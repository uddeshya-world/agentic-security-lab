## The five parts

```
  user ──▶ RAG ──▶ PLANNER (LLM) ──▶ EXECUTOR ──▶ TOOLS ──▶ world
           │                                        │
       knowledge                              db · email · files
        (Chroma)                              (real side effects)
```

| Part | What it does | Why an attacker cares |
|------|--------------|-----------------------|
| **RAG** | Retrieves documents to give the model context | An input channel — poison a doc, poison the context |
| **Planner** | LLM that decides which tools to call | If steered, it *authors* the attack for you |
| **Executor** | Runs the planner's tool calls | The last place to say "no" before real effects |
| **Tools** | SQL, email, file — real side effects | Where damage actually happens |
| **Memory** | Persists across turns and sessions | Poison here outlives the session |

Read the map top to bottom. The planner is the "brain," but the **executor is
where security lives** — because the brain can be lied to.
