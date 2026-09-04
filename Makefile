# GNU Make targets, used when `make` is present (e.g. WSL/git-bash with make
# installed). run.ps1 / run.sh are the actually-relied-upon entrypoints on
# this Windows host -- see plan section 7, risk #6.

.PHONY: up up-langfuse down wait smoke pull-model attack-01 metrics-01 logs

up:
	docker compose up -d ollama ollama-init mailhog db-tool email-tool file-tool agent

up-langfuse:
	docker compose -f docker-compose.yml -f docker-compose.langfuse.yml up -d

down:
	docker compose -f docker-compose.yml -f docker-compose.langfuse.yml down

wait:
	python scripts/wait_for_services.py

smoke:
	pytest tests/test_smoke.py -v

pull-model:
	python scripts/pull_model.py

attack-01:
	python -m attacks.m01.attack_param_manipulation
	python -m attacks.m01.attack_retrieval_poisoning
	python -m attacks.m01.attack_cross_tool_exfil

metrics-01:
	python -m metrics.m01.run_metrics

logs:
	docker compose logs -f $(SERVICE)
