## Confirm the lab is up

Bring the stack up if you have not already:

```bash
docker compose up -d
```

Then check that the agent and its tools are healthy:

```bash
curl -s http://127.0.0.1:8000/lab/status
```

You are looking for a `mode_summary` and three tools reporting `ok`. The
**Check** button below asks the lab the same question and confirms every tool
server is reachable.

> If a tool is down, run `docker compose ps` and `docker compose logs <service>`.
> Nothing else in this Area will work until the tools are healthy.
