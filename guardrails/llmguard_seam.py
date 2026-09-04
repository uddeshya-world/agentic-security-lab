"""Integration seam for LLM Guard. No-op passthrough -- NOT enabled in
modules 0/1. Mirrors nemo_seam.py's shape; a future module can wire either
or both in without touching call sites.
"""


def scan_input(prompt: str) -> str:
    return prompt


def scan_output(response: str) -> str:
    return response
