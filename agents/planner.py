"""Planner node. Vulnerable: output is trusted verbatim by the executor with
no schema check (that check only exists behind SECURE_MODE in
defenses/01/schema_validation.py).
"""
from pathlib import Path

from agents.llm_client import chat, extract_json_block
from agents.state import AgentState
from observability.tracing import trace_agent_step

PROMPT_PATH = Path(__file__).parent / "prompts" / "planner_system.txt"


@trace_agent_step("planner")
def planner_node(state: AgentState) -> AgentState:
    template = PROMPT_PATH.read_text()
    system_prompt = template.format(
        rag_context="\n---\n".join(state.get("rag_context", [])) or "(none)",
        memory_context=str(state.get("memory_context", {})) or "(none)",
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": state["user_request"]},
    ]
    try:
        message = chat(messages)
        content = message.get("content") or ""
    except Exception as e:
        content = f"(planner LLM error: {e})"
        message = {"content": content}

    parsed = extract_json_block(content) if content else None
    steps = None
    if isinstance(parsed, dict):
        steps = parsed.get("steps")
        # Tolerate weird keys from partial JSON
        if steps is None:
            for k, v in parsed.items():
                if str(k).strip("\"'") == "steps":
                    steps = v
                    break
    if not isinstance(steps, list) or not steps:
        steps = [
            {
                "tool": "answer",
                "args": {
                    "text": content
                    or "Planner could not produce a structured plan (LLM unavailable or bad JSON)."
                },
                "reason": "fallback",
            }
        ]

    state["plan"] = steps
    state["current_step"] = 0
    state["executor_results"] = []
    return state
