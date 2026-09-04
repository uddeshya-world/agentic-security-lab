#!/usr/bin/env bash
# Bash/git-bash equivalent of every Makefile target. Primary entrypoint on
# this machine (no `make` installed) -- see plan section 7, risk #6.
set -euo pipefail
cmd="${1:-help}"

case "$cmd" in
  up)
    docker compose up -d ollama ollama-init mailhog db-tool email-tool file-tool agent
    echo ""
    echo "Lab Console:  http://127.0.0.1:8000/lab/ui/"
    echo "MailHog:      http://127.0.0.1:8025"
    echo "Module 1 sims do NOT need host Ollama (internal only)."
    ;;
  up-langfuse)
    docker compose -f docker-compose.yml -f docker-compose.langfuse.yml up -d
    ;;
  down)
    docker compose -f docker-compose.yml -f docker-compose.langfuse.yml down
    ;;
  wait)
    python scripts/wait_for_services.py
    ;;
  smoke)
    pytest tests/test_smoke.py -v
    ;;
  pull-model)
    python scripts/pull_model.py
    ;;
  attack-01)
    python -m attacks.m01.attack_param_manipulation
    python -m attacks.m01.attack_retrieval_poisoning
    python -m attacks.m01.attack_cross_tool_exfil
    ;;
  metrics-01)
    python -m metrics.m01.run_metrics
    ;;
  logs)
    docker compose logs -f "${2:-agent}"
    ;;
  *)
    echo "Usage: ./run.sh {up|up-langfuse|down|wait|smoke|pull-model|attack-01|metrics-01|logs [service]}"
    ;;
esac
