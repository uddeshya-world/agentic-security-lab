# PowerShell equivalent of every Makefile target. Primary entrypoint on this
# machine (no `make` installed) -- see plan section 7, risk #6.
param([string]$Cmd = "help", [string]$Service = "agent")

switch ($Cmd) {
    "up" {
        docker compose up -d ollama ollama-init mailhog db-tool email-tool file-tool agent
        Write-Host ""
        Write-Host "Lab Console:  http://127.0.0.1:8000/lab/ui/"
        Write-Host "MailHog:      http://127.0.0.1:8025"
        Write-Host "For faster LLM: .\run.ps1 -Cmd up-host-ollama  (use GPU via Windows Ollama)"
        Write-Host "Or NVIDIA Docker GPU: .\run.ps1 -Cmd up-gpu"
    }
    "up-gpu" {
        # NVIDIA GPU inside Docker (needs nvidia-smi + Docker GPU support)
        docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d ollama ollama-init mailhog db-tool email-tool file-tool agent
        Write-Host "GPU overlay applied. Verify: docker compose exec ollama nvidia-smi"
        Write-Host "Lab Console: http://127.0.0.1:8000/lab/ui/"
    }
    "up-host-ollama" {
        # Fastest path on most Windows laptops: Ollama on host uses GPU, agent in Docker
        Write-Host "Start Windows Ollama first, then: ollama pull qwen2.5:1.5b-instruct"
        docker compose -f docker-compose.yml -f docker-compose.host-ollama.yml up -d mailhog db-tool email-tool file-tool agent
        Write-Host ""
        Write-Host "Agent uses host Ollama at host.docker.internal:11434"
        Write-Host "Lab Console: http://127.0.0.1:8000/lab/ui/"
        Write-Host "Check ollama pill green after a few seconds."
    }
    "up-langfuse" {
        docker compose -f docker-compose.yml -f docker-compose.langfuse.yml up -d
    }
    "down" {
        docker compose -f docker-compose.yml -f docker-compose.langfuse.yml down
    }
    "wait" {
        python scripts/wait_for_services.py
    }
    "smoke" {
        pytest tests/test_smoke.py -v
    }
    "pull-model" {
        python scripts/pull_model.py
    }
    "attack-01" {
        python -m attacks.m01.attack_param_manipulation
        python -m attacks.m01.attack_retrieval_poisoning
        python -m attacks.m01.attack_cross_tool_exfil
    }
    "metrics-01" {
        python -m metrics.m01.run_metrics
    }
    "logs" {
        docker compose logs -f $Service
    }
    default {
        Write-Host "Usage: .\run.ps1 -Cmd {up|up-gpu|up-host-ollama|up-langfuse|down|wait|smoke|pull-model|attack-01|metrics-01|logs} [-Service name]"
    }
}
