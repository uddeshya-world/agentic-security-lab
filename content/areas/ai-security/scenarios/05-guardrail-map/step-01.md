## Eight hops, one data path

```
user ─▶ [1] INPUT DLP ─▶ [2] RAG + CONTEXT DLP ─▶ [3] PLANNER ─▶ [4] IDENTITY
         C21                  C6 + C21                   C7            session
         ─▶ [5] SCHEMA ─▶ [6] PRIVILEGE ─▶ [7] TOOL DLP + HITL + EGRESS ─▶ [8] OUTPUT DLP ─▶ world
              C2              C1               C21 + C5 + C4                    C21
```

| # | Layer | Threat it stops | Control | Lab |
|---|-------|-----------------|---------|-----|
| 1 | Input DLP | SSN/PAN/secrets in the prompt | C21 classify → block | `scan_data(channel='input')` |
| 2 | RAG + context DLP | Indirect PI; PII in chunks | C6 + C21 | `rag/retriever.py` |
| 3 | Planner output | Model authors a harmful plan | C7 never trust the plan | `agents/executor.py` |
| 4 | Identity | Confused deputy, wrong principal | Session `customer_id` | A6 |
| 5 | Schema / args | `filter=1=1`, `../` | C2 allow-list | `schema_validation.py` |
| 6 | Least privilege | Over-broad reads | C1 parameterized SQL, path jail | `least_privilege.py` |
| 7 | Tool DLP + HITL + egress | PII in results; unattended send; wrong domain | C21 + C5 + C4 | A4 + A5 |
| 8 | Output DLP | Model recites PII | C21 mask/block | `scan_data(channel='output')` |

Read it twice. Every Core attack in this Area was one hop with no control on it.
