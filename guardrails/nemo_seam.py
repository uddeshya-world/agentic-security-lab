"""Integration seam for NeMo Guardrails. No-op passthrough -- NOT enabled in
modules 0/1. A future module wires a real NeMo Guardrails rails config in
here; call sites (planner.py / executor.py, wrapping LLM input/output) don't
need to change.
"""


def pre_check(prompt: str) -> str:
    """Runs before the prompt is sent to the LLM. Passthrough for now."""
    return prompt


def post_check(response: str) -> str:
    """Runs after the LLM responds. Passthrough for now."""
    return response
