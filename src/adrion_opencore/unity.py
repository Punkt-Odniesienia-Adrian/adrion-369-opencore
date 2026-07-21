"""
ADRION 369 Open-Core — Unity Module

Checks whether a proposed agent decision is consistent with the agent's
own prior decisions on comparable inputs, flagging contradictions before
they reach the user.

Reference implementation of the "Unity" guardian check from the
ADRION 369 ethics-governance layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class ConsistencyResult:
    consistent: bool
    conflicting_with: list[int]
    reason: str


class UnityChecker:
    """
    Tracks prior (input_signature, decision) pairs and flags new
    decisions that contradict earlier ones for similar inputs.
    """

    def __init__(self, similarity_fn: Optional[Callable[[Any, Any], bool]] = None) -> None:
        self._history: list[tuple[Any, Any]] = []
        self._similarity_fn = similarity_fn or (lambda a, b: a == b)

    def check(self, input_signature: Any, proposed_decision: Any) -> ConsistencyResult:
        conflicts = [
            i
            for i, (sig, dec) in enumerate(self._history)
            if self._similarity_fn(sig, input_signature) and dec != proposed_decision
        ]
        if conflicts:
            return ConsistencyResult(
                consistent=False,
                conflicting_with=conflicts,
                reason=f"Decision contradicts {len(conflicts)} prior decision(s) on similar input.",
            )
        return ConsistencyResult(consistent=True, conflicting_with=[], reason="No conflicts found.")

    def record(self, input_signature: Any, decision: Any) -> None:
        self._history.append((input_signature, decision))
