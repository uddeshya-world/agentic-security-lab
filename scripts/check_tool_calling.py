"""Checkpoint 1: model tool-calling viability check. Run BEFORE building
agents/graph.py -- if the model doesn't reliably emit well-formed
`tool_calls`, agents/llm_client.py's extract_json_block() fallback (fenced
JSON / structured-output prompting) is used instead, and agents/planner.py
is written around that fallback from the start.
"""
import json
import os
import sys

import httpx

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b-instruct")

TOOL_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "db_tool",
            "description": "Query synthetic customers/orders data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table": {"type": "string"},
                    "filter": {"type": "string"},
                },
                "required": ["table", "filter"],
            },
        },
    }
]


def main() -> int:
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "List all customers in the database using the db_tool.",
            }
        ],
        "tools": TOOL_SCHEMA,
        "stream": False,
    }
    print(f"Sending chat request to {OLLAMA_BASE_URL} with model={MODEL} ...")
    resp = httpx.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=300.0)
    resp.raise_for_status()
    data = resp.json()
    message = data.get("message", {})
    print("Raw message:", json.dumps(message, indent=2))

    tool_calls = message.get("tool_calls")
    if tool_calls and isinstance(tool_calls, list) and len(tool_calls) > 0:
        print(f"NATIVE_TOOL_CALLING_WORKS: {len(tool_calls)} tool_call(s) returned")
        return 0
    else:
        print("NATIVE_TOOL_CALLING_ABSENT: falling back to structured-output prompting")
        return 1


if __name__ == "__main__":
    sys.exit(main())
