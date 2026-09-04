"""Idempotent `ollama pull` -- mirrors what the ollama-init compose service
does, kept as a standalone script for re-running manually if the model tag
changes or the volume gets wiped.
"""
import os
import sys

import httpx

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b-instruct")


def main() -> int:
    print(f"Pulling {MODEL} from {OLLAMA_BASE_URL} ...")
    with httpx.stream(
        "POST", f"{OLLAMA_BASE_URL}/api/pull", json={"name": MODEL}, timeout=None
    ) as resp:
        for line in resp.iter_lines():
            if line:
                print(line)
    print("PULL_DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
