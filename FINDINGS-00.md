# Findings -- Module 0: Foundation build notes

## Checkpoint 1: model tool-calling viability

- Model: `qwen2.5:3b-instruct` (1.9GB, pulled via `ollama-init`).
- Native Ollama tool-calling (`/api/chat` with `tools=[...]`) confirmed
  **working** -- the model returned a well-formed `tool_calls` response on
  the first try:
  ```json
  {"role": "assistant", "content": "", "tool_calls": [{"id": "call_hgsj3g69",
    "function": {"name": "db_tool", "arguments": {"table": "customers"}}}]}
  ```
  (Verification script: `scripts/check_tool_calling.py`.)
- Decision: despite native tool-calling working, `agents/planner.py` uses
  **prompt-based JSON extraction** (a fenced ` ```json ` block via
  `agents/llm_client.py::extract_json_block`), not Ollama's native
  `tool_calls` field. Reason: the planner's output schema is a multi-step
  plan (`{"steps": [{"tool": ..., "args": ..., "reason": ...}]}`), including
  a non-tool "answer" pseudo-step -- richer than Ollama's native single
  tool-call-per-turn shape. The viability check's real purpose -- confirming
  this model reliably follows structured-output instructions at all -- is
  satisfied either way; native tool-calling success is strong evidence the
  same model will follow the (similarly-structured) fenced-JSON plan format.
- Practical note: first inference on this CPU-only host took >120s (model
  load into RAM) but completed in ~300s region; default timeouts in
  `agents/llm_client.py` and `scripts/check_tool_calling.py` are set to
  120s/300s respectively to accommodate this. If this proves too slow once
  the full graph is exercised end-to-end (Checkpoint 4), consider warming
  the model with a no-op request at agent startup.
- Ollama's port (11434) was temporarily published to the host
  (`docker-compose.yml`) to run this check from outside the Docker network;
  reverted to internal-only afterward, consistent with the original design
  (agent container reaches Ollama via the internal network at
  `http://ollama:11434`).
