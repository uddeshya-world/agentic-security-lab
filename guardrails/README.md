# Guardrails seam

`nemo_seam.py` and `llmguard_seam.py` are no-op passthrough hooks for
NeMo Guardrails and LLM Guard respectively. Neither is enabled in modules
0/1 -- see PROMPT 5 (Production Guardrails & Observability) in the prompt
pack for the module that wires real guardrail pipelines in here.
