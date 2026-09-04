from langgraph.graph import END, START, StateGraph

from agents.executor import executor_node, should_continue
from agents.planner import planner_node
from agents.state import AgentState
from memory import store as memory_store
from observability.tracing import trace_agent_step
from rag.retriever import retrieve


@trace_agent_step("retrieve_context")
def retrieve_context_node(state: AgentState) -> AgentState:
    state["rag_context"] = retrieve(state["user_request"])
    state["memory_context"] = memory_store.read_session(state["session_id"])
    return state


@trace_agent_step("finalize")
def finalize_node(state: AgentState) -> AgentState:
    answer_parts = [
        r["result"] if isinstance(r["result"], str) else str(r["result"])
        for r in state["executor_results"]
        if r["tool"] == "answer"
    ]
    final_answer = "\n".join(answer_parts) if answer_parts else "(no direct answer produced)"
    state["final_answer"] = final_answer

    # Unvalidated write-back -- intentional seam for module 4 (memory poisoning).
    memory_store.write_long_term(state["session_id"], final_answer)
    return state


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("retrieve_context", retrieve_context_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "retrieve_context")
    graph.add_edge("retrieve_context", "planner")
    graph.add_edge("planner", "executor")
    graph.add_conditional_edges(
        "executor", should_continue, {"executor": "executor", "finalize": "finalize"}
    )
    graph.add_edge("finalize", END)

    return graph.compile()


_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_agent(session_id: str, user_request: str) -> AgentState:
    initial_state: AgentState = {
        "session_id": session_id,
        "user_request": user_request,
        "plan": [],
        "current_step": 0,
        "executor_results": [],
        "rag_context": [],
        "memory_context": {},
        "final_answer": None,
        "trace_id": "",
    }
    graph = get_graph()
    return graph.invoke(initial_state)
