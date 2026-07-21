"""
ADRION 369 Open-Core — Transparency Module

Provides an append-only, hash-chained audit log for AI agent decisions.
Every entry is cryptographically linked to the previous one (SHA-256),
so tampering with historical entries is immediately detectable.

Reference implementation of the "Transparency" guardian check from the
ADRION 369 ethics-governance layer. The enterprise suite adds veto-
capable guardians (privacy, nonmaleficence) and the full 162-dimensional
decision space on top of this log — available under a separate license.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AuditEntry:
    index: int
    timestamp: float
    actor: str
    action: str
    payload: dict
    prev_hash: str
    hash: str = field(init=False)

    def __post_init__(self) -> None:
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        body = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "actor": self.actor,
                "action": self.action,
                "payload": self.payload,
                "prev_hash": self.prev_hash,
            },
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(body).hexdigest()


class TransparencyLog:
    """Append-only, hash-chained decision log."""

    GENESIS_HASH = "0" * 64

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def record(self, actor: str, action: str, payload: dict[str, Any] | None = None) -> AuditEntry:
        prev_hash = self._entries[-1].hash if self._entries else self.GENESIS_HASH
        entry = AuditEntry(
            index=len(self._entries),
            timestamp=time.time(),
            actor=actor,
            action=action,
            payload=payload or {},
            prev_hash=prev_hash,
        )
        self._entries.append(entry)
        return entry

    def verify_chain(self) -> bool:
        """Return True if no entry in the chain has been tampered with."""
        expected_prev = self.GENESIS_HASH
        for entry in self._entries:
            if entry.prev_hash != expected_prev or entry.hash != entry._compute_hash():
                return False
            expected_prev = entry.hash
        return True

    def __len__(self) -> int:
        return len(self._entries)

    def export(self) -> list[dict]:
        return [
            {
                "index": e.index,
                "timestamp": e.timestamp,
                "actor": e.actor,
                "action": e.action,
                "payload": e.payload,
                "prev_hash": e.prev_hash,
                "hash": e.hash,
            }
            for e in self._entries
        ]
