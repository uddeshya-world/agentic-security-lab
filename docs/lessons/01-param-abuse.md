# Lesson A1 — Parameter abuse

**Console:** open Lab Console → **A1 — Parameter abuse** → Run simulation.

## Story

Agent tools that accept raw SQL fragments or join file paths without a jail recreate classic appsec bugs behind an “AI” facade.

## Vulnerable outcome

- `db_tool` + `filter=1=1` returns multiple synthetic customers  
- (Optional) path traversal may read outside `/workspace` depending on container FS  

## Secure outcome

- DB requires scoped `customer_id`  
- Path escapes rejected  

## Design rule

Parameterize queries; jail paths; validate args at the executor before invoke.

## Code

- `tools/db_tool/queries.py`  
- `tools/file_tool/server.py`  
- `defenses/m01/schema_validation.py`  
