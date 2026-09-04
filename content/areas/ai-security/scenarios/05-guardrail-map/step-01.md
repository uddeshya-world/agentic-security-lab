## Six layers, one data path

```
user ─▶ [1] RAG ─▶ [2] PLANNER ─▶ [3] SCHEMA ─▶ [4] PRIVILEGE ─▶ [5] HITL ─▶ [6] TOOL POLICY ─▶ world
        C6           C7             C2             C1               C5           C4
```

| # | Layer | Threat it stops | Control | Lab implementation |
|---|-------|-----------------|---------|--------------------|
| 1 | Context / RAG | indirect prompt injection | C6 trust filter | `rag/retriever.py` |
| 2 | Planner output | model emits malicious calls | C7 re-validate plan | `agents/executor.py` |
| 3 | Schema / args | injection-shaped parameters | C2 allow-list | `defenses/m01/schema_validation.py` |
| 4 | Least privilege | over-broad reads/writes | C1 scoped SQL, path jail | `defenses/m01/least_privilege.py` |
| 5 | Side-effect / HITL | unattended email/write | C5 approval gate | `defenses/m01/approval_gate.py` |
| 6 | Tool policy | valid call, wrong target | C4 egress allow-list | `tools/email_tool/server.py` |

Read it twice. Every attack in this Area was one hop with no control on it.
