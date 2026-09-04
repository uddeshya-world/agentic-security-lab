# How to prevent these attacks (student blue-team guide)

Red team without blue team is incomplete. After each attack lands, you must be able to answer:

1. **What failed?** (root cause)  
2. **What control stops it?**  
3. **Where is it implemented in this lab?** (`SECURE_MODE`)  
4. **What would production do beyond the lab?**

## Universal rule

> **Assume the LLM can be tricked.**  
> Authorization and safety live in **code** (executor + tools + data policy), not only in prompts.

```
User / RAG / web
      │
      ▼
  Planner (LLM)  ← untrusted proposals
      │
      ▼
  Executor       ← C2 schema, C5 HITL, C7 never trust plan
      │
      ▼
  Tools          ← C1 SQL, C3 path jail, C4 email allow-list
      │
      ▼
  Side effects   (DB, MailHog, files)
```

## Attack → remediation quick map

| Attack | Root cause | Fix (controls) | Lab proof |
|--------|------------|----------------|-----------|
| Dump customers (`filter=1=1`) | Raw SQL fragment | **C1** parameterized scope + **C2** schema | SECURE_MODE error: `customer_id required` |
| Path `../etc/hostname` | Naive path join | **C3** path jail + **C2** | `escapes workspace jail` |
| Email to external | No domain allow-list / no HITL | **C4** + **C5** | domain not allow-listed / ApprovalDenied |
| Shipping Q → silent export | Poison in RAG trusted as orders | **C6** trust filter + still **C1/C4/C5** | untrusted chunks dropped + tool blocks |

## Control catalog (what you are learning)

| ID | Control | OWASP / ASI |
|----|---------|-------------|
| C1 | Parameterized / scoped DB | LLM02, LLM06, ASI02 |
| C2 | Tool arg schema allow-list at executor | LLM06, ASI02, ASI07 |
| C3 | Filesystem jail | LLM06, ASI02 |
| C4 | Email/egress domain allow-list | LLM02, ASI02 |
| C5 | HITL for side-effect tools | LLM06, ASI02 |
| C6 | RAG trust / provenance filter | LLM01, LLM04, LLM08, ASI01, ASI06 |
| C7 | Never treat planner output as authz | LLM01, LLM06, ASI07 |

## How to practice in the UI

1. Fire attack in **VULNERABLE** mode → exploit lands.  
2. Open **Remediation** panel → read immediate fix + production checklist.  
3. Set `SECURE_MODE=true`, recreate agent + tools.  
4. Fire **same** attack → DEFENSE lines.  
5. Open listed **lab code** files and match error text to the control.

## Toggle secure mode

```powershell
$env:SECURE_MODE="true"
docker compose up -d --force-recreate agent db-tool email-tool file-tool

$env:SECURE_MODE="false"
docker compose up -d --force-recreate agent db-tool email-tool file-tool
```

API: `GET /lab/curriculum` and `GET /lab/remediation/{exploit_id}`.
