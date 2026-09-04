## Same stack, other side of the glass

You already know what happened, which is a luxury you will never have at work.
Use it: this is where you learn what an incident *looks like* in evidence, by
comparing the evidence against a truth you already hold.

Three surfaces record something here:

| Surface | Where | What it holds |
|---|---|---|
| Lab event log | `GET /lab/events` | Every phase of every run: `plan`, `tool`, `sql`, `defense`, `result` |
| Mail sink | `http://127.0.0.1:8025`, API `/api/v2/messages` | Every message the email tool actually sent, with the full body |
| Tool servers | `docker compose logs db-tool email-tool file-tool` | Request-level detail per tool |

The event log is the closest thing here to a SIEM. It is not one. No retention
policy, no normalisation, and no identity on any row — which matters more than it
sounds, and matters in scenario 2.
