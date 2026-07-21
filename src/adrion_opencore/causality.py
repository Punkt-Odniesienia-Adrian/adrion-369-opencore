"""
ADRION 369 Open-Core — Causality Module

Records the causal chain behind an agent decision: which inputs, which
intermediate reasoning steps, and which rule fired — so "why did the
agent do X" has a concrete, inspectable answer instead of a black box.

Reference implementation of the "Causality" guardian check from the
ADRION 369 ethics-governance layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReasoningStep:
    description: str
    inputs: dict[str, Any]
    output: Any


@dataclass
class CausalTrace:
    decision: str
    steps: list[ReasoningStep] = field(default_factory=list)

    def add_step(self, description: str, inputs: dict[str, Any], output: Any) -> None:
        self.steps.append(ReasoningStep(description=description, inputs=inputs, output=output))

    def explain(self) -> str:
        """Human-readable explanation of the decision path."""
        lines = [f"Decision: {self.decision}"]
        for i, step in enumerate(self.steps, start=1):
            lines.append(f"  {i}. {step.description} -> {step.output}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "steps": [
                {"description": s.description, "inputs": s.inputs, "output": s.output}
                for s in self.steps
            ],
        }


class CausalityTracker:
    """Collects causal traces for a batch of agent decisions."""

    def __init__(self) -> None:
        self._traces: dict[str, CausalTrace] = {}

    def start_trace(self, decision_id: str, decision: str) -> CausalTrace:
        trace = CausalTrace(decision=decision)
        self._traces[decision_id] = trace
        return trace

    def get_trace(self, decision_id: str) -> CausalTrace | None:
        return self._traces.get(decision_id)
