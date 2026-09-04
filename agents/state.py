from typing import TypedDict


class AgentState(TypedDict):
    session_id: str
    user_request: str
    plan: list[dict]
    current_step: int
    executor_results: list[dict]
    rag_context: list[str]
    memory_context: dict
    final_answer: str | None
    trace_id: str
