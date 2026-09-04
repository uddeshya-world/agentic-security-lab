"""Executor node. Vulnerable path trusts planner steps with no revalidation.

When SECURE_MODE=true, Module 1 defenses attach at this choke point:
schema validation → least privilege → simulated HITL approval → isolated invoke.
"""
from __future__ import annotations

import os

from agents.state import AgentState
from defenses.config import is_secure
from observability.tracing import trace_tool_call
from policy.opa_seam import check_policy
from tools import registry

MAX_PLAN_STEPS = int(os.environ.get("MAX_PLAN_STEPS", "8"))


@trace_tool_call("executor_step")
def _run_step(step: dict) -> dict:
    tool = step.get("tool", "answer")
    args = dict(step.get("args") or {})

    if tool == "answer":
        return {"tool": "answer", "result": args.get("text", "")}

    if is_secure():
        try:
            from defenses.m01.approval_gate import require_approval
            from defenses.m01.isolation import run_isolated
            from defenses.m01.least_privilege import apply_least_privilege
            from defenses.m01.schema_validation import validate_step

            validate_step(tool, args)
            args = apply_least_privilege(tool, args)
            require_approval(tool, args)

            if not check_policy(tool, args):
                return {
                    "tool": tool,
                    "result": {"error": "policy denied", "secure_mode": True},
                }

            result = run_isolated(lambda: registry.invoke(tool, args), tool_name=tool)
            return {"tool": tool, "result": result}
        except Exception as e:
            return {
                "tool": tool,
                "result": {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "secure_mode": True,
                },
            }

    # Vulnerable path: always-allow policy stub; no schema revalidation.
    check_policy(tool, args)

    try:
        result = registry.invoke(tool, args)
    except Exception as e:
        result = {"error": str(e)}
    return {"tool": tool, "result": result}


def executor_node(state: AgentState) -> AgentState:
    plan = state["plan"]
    idx = state["current_step"]
    if idx >= len(plan):
        return state
    if idx >= MAX_PLAN_STEPS:
        state["executor_results"].append(
            {
                "tool": "answer",
                "result": f"(stopped: exceeded MAX_PLAN_STEPS={MAX_PLAN_STEPS})",
            }
        )
        state["current_step"] = len(plan)
        return state
    step = plan[idx]
    outcome = _run_step(step)
    state["executor_results"].append(outcome)
    state["current_step"] = idx + 1
    return state


def should_continue(state: AgentState) -> str:
    if state["current_step"] < len(state["plan"]) and state["current_step"] < MAX_PLAN_STEPS:
        return "executor"
    return "finalize"
