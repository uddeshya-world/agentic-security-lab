# Fast-track the LLM (GPU / small model)

Your lab was timing out because **compose Ollama was almost certainly on CPU**, and `qwen2.5:3b` is heavy on CPU.

## Ranked options (fastest first)

### 1) Host Ollama + GPU (recommended on Windows laptops)

Native Ollama uses your GPU more reliably than Docker on Windows.

```powershell
# Install from https://ollama.com/download if needed

# Smaller/faster model (good for tool JSON)
ollama pull qwen2.5:1.5b-instruct

# Optional: keep it hot
ollama run qwen2.5:1.5b-instruct "ok"

# Lab without dockerized Ollama
cd agentic-security-lab
# in .env:
#   OLLAMA_MODEL=qwen2.5:1.5b-instruct
.\run.ps1 -Cmd up-host-ollama
```

Agent talks to `http://host.docker.internal:11434`.  
Console **ollama** pill should go green.

**Check GPU in host Ollama:** while a request runs, Task Manager → Performance → GPU (CUDA / 3D usage should bump). Or with NVIDIA: `nvidia-smi`.

---

### 2) NVIDIA GPU *inside* Docker

Needs:

1. NVIDIA driver + `nvidia-smi` works in PowerShell  
2. Docker Desktop → Settings → Resources → enable GPU / WSL2  
3. Then:

```powershell
.\run.ps1 -Cmd up-gpu
docker compose exec ollama nvidia-smi
```

If `nvidia-smi` fails inside the container, Docker is not seeing the GPU — use option 1.

---

### 3) Stay on Docker CPU but go smaller/faster

In `.env`:

```env
OLLAMA_MODEL=qwen2.5:1.5b-instruct
# or even: llama3.2:1b
OLLAMA_TIMEOUT_S=180
LIVE_ATTACK_LLM_TIMEOUT_S=90
```

Then:

```powershell
docker compose up -d --force-recreate ollama ollama-init agent
# wait for pull
docker compose logs -f ollama-init
```

---

## Model size vs speed (rule of thumb)

| Model | VRAM / feel | Speed |
|-------|-------------|--------|
| `llama3.2:1b` / `qwen2.5:0.5b` | Tiny | Fastest, weaker tool JSON |
| **`qwen2.5:1.5b-instruct`** | Small | **Best lab default** |
| `qwen2.5:3b-instruct` | Medium | OK on GPU, slow on CPU |
| 7B+ | Larger | Only if GPU has headroom |

---

## Keep model warm

- Host: leave Ollama running; run a tiny prompt after boot  
- Compose: `OLLAMA_KEEP_ALIVE=30m` is already set on the ollama service  

---

## How you know it worked

1. UI **ollama** pill green  
2. Fire attack → banner says **`live_ollama`** (not executor fallback) within ~10–60s on GPU  
3. Plan shows `db_tool` etc. from the model  

If you still see “LLM timed out… executor fallback”, GPU is not in use or the model is still too big — switch to **1.5b + host Ollama**.
