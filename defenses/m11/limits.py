"""LLM06 defense: resource limits — step cap, budget, loop detection, rate limit.

The lab already caps plan length (``MAX_PLAN_STEPS``), which is why LLM06 was only
*partially* covered. A step cap alone does not stop:

- **denial of wallet** — many cheap-looking steps that each burn tokens/API spend;
- **tool-call loops** — the same call repeated forever (or two steps ping-ponging);
- **burst abuse** — one session issuing calls far faster than any human workflow.

``ResourceGuard`` enforces all four limits together and explains which one fired,
so the lesson shows *which* control stopped the runaway rather than just "blocked".
"""
from __future__ import annotations

from collections import Counter


class LimitExceeded(Exception):
    def __init__(self, control: str, message: str):
        super().__init__(message)
        self.control = control


class ResourceGuard:
    def __init__(self, *, max_steps: int = 8, max_cost_units: int = 100,
                 max_repeats: int = 3, max_calls_per_window: int = 20):
        self.max_steps = max_steps
        self.max_cost_units = max_cost_units
        self.max_repeats = max_repeats
        self.max_calls_per_window = max_calls_per_window
        self.steps = 0
        self.cost = 0
        self.calls_in_window = 0
        self._signatures: Counter[str] = Counter()

    @staticmethod
    def _signature(tool: str, args: dict) -> str:
        return f"{tool}:{sorted((args or {}).items())}"

    def check(self, tool: str, args: dict, *, cost: int = 5) -> None:
        """Raise LimitExceeded naming the control that fired; otherwise record usage."""
        if self.steps + 1 > self.max_steps:
            raise LimitExceeded("step-cap", f"plan exceeded {self.max_steps} steps")

        if self.calls_in_window + 1 > self.max_calls_per_window:
            raise LimitExceeded("rate-limit",
                                f"more than {self.max_calls_per_window} calls in the window")

        sig = self._signature(tool, args)
        if self._signatures[sig] + 1 > self.max_repeats:
            raise LimitExceeded("loop-detector",
                                f"identical call repeated more than {self.max_repeats} times: {tool}")

        if self.cost + cost > self.max_cost_units:
            raise LimitExceeded("cost-budget",
                                f"session budget of {self.max_cost_units} units exhausted")

        self.steps += 1
        self.calls_in_window += 1
        self.cost += cost
        self._signatures[sig] += 1

    def usage(self) -> dict:
        return {"steps": self.steps, "cost_units": self.cost,
                "calls_in_window": self.calls_in_window,
                "distinct_calls": len(self._signatures)}
