"""
ADRION 369 Open-Core — Transparency Module Test Suite
=====================================================
28 tests covering: hash integrity, chain verification, tamper detection,
export contract, edge cases, multiple actors, large chains, unicode payloads.
"""

from __future__ import annotations

import hashlib
import json
import time

import pytest

from adrion_opencore.transparency import AuditEntry, TransparencyLog


# ─────────────────────────── CONSTRUCTION ───────────────────────────


def test_empty_log_verifies():
    log = TransparencyLog()
    assert log.verify_chain() is True


def test_new_log_length_zero():
    assert len(TransparencyLog()) == 0


def test_genesis_hash_constant():
    assert TransparencyLog.GENESIS_HASH == "0" * 64


def test_genesis_hash_is_64_chars():
    assert len(TransparencyLog.GENESIS_HASH) == 64


# ─────────────────────────── RECORD ────────────────────────────────


def test_record_increments_length():
    log = TransparencyLog()
    log.record("agent", "action_a")
    assert len(log) == 1
    log.record("agent", "action_b")
    assert len(log) == 2


def test_first_entry_prev_hash_is_genesis():
    log = TransparencyLog()
    entry = log.record("agent-1", "start")
    assert entry.prev_hash == TransparencyLog.GENESIS_HASH


def test_second_entry_prev_hash_links_to_first():
    log = TransparencyLog()
    e1 = log.record("agent-1", "action_a")
    e2 = log.record("agent-1", "action_b")
    assert e2.prev_hash == e1.hash


def test_entry_index_sequential():
    log = TransparencyLog()
    for i in range(5):
        entry = log.record("a", f"action_{i}")
        assert entry.index == i


def test_record_returns_audit_entry():
    log = TransparencyLog()
    entry = log.record("agent", "action")
    assert isinstance(entry, AuditEntry)


def test_record_stores_actor_and_action():
    log = TransparencyLog()
    entry = log.record("myagent", "myaction", {"k": "v"})
    assert entry.actor == "myagent"
    assert entry.action == "myaction"


def test_record_stores_payload():
    log = TransparencyLog()
    payload = {"amount": 42, "currency": "EUR", "approved": True}
    entry = log.record("agent", "payment", payload)
    assert entry.payload == payload


def test_record_empty_payload_default():
    log = TransparencyLog()
    entry = log.record("agent", "action")
    assert entry.payload == {}


def test_record_none_payload_becomes_empty_dict():
    log = TransparencyLog()
    entry = log.record("agent", "action", None)
    assert entry.payload == {}


# ─────────────────────────── HASH INTEGRITY ────────────────────────


def test_entry_hash_is_sha256():
    log = TransparencyLog()
    entry = log.record("agent", "action")
    # SHA-256 hex digest is always 64 hex characters
    assert len(entry.hash) == 64
    assert all(c in "0123456789abcdef" for c in entry.hash)


def test_entry_hash_deterministic_for_same_state():
    log = TransparencyLog()
    entry = log.record("agent", "action", {"x": 1})
    expected = entry._compute_hash()
    assert entry.hash == expected


def test_verify_chain_single_entry():
    log = TransparencyLog()
    log.record("agent", "action")
    assert log.verify_chain() is True


def test_verify_chain_ten_entries():
    log = TransparencyLog()
    for i in range(10):
        log.record("agent", f"step_{i}", {"i": i})
    assert log.verify_chain() is True


def test_verify_chain_multiple_actors():
    log = TransparencyLog()
    log.record("guardian-g7", "veto_check", {"input": "sensitive_data"})
    log.record("guardian-g8", "harm_check", {"input": "action"})
    log.record("executor", "proceed", {"result": "approved"})
    assert log.verify_chain() is True


# ─────────────────────────── TAMPER DETECTION ──────────────────────


def test_tamper_payload_breaks_chain():
    log = TransparencyLog()
    entry = log.record("agent", "approve", {"amount": 100})
    entry.payload["amount"] = 999_999
    assert log.verify_chain() is False


def test_tamper_actor_breaks_chain():
    log = TransparencyLog()
    entry = log.record("legitimate-agent", "action")
    entry.actor = "malicious-agent"
    assert log.verify_chain() is False


def test_tamper_action_breaks_chain():
    log = TransparencyLog()
    entry = log.record("agent", "read_only")
    entry.action = "delete_all"
    assert log.verify_chain() is False


def test_tamper_prev_hash_breaks_chain():
    log = TransparencyLog()
    log.record("agent", "first")
    e2 = log.record("agent", "second")
    e2.prev_hash = "a" * 64
    assert log.verify_chain() is False


def test_tamper_mid_chain_breaks_chain():
    log = TransparencyLog()
    log.record("agent", "step_1")
    mid = log.record("agent", "step_2")
    log.record("agent", "step_3")
    mid.payload["injected"] = True
    assert log.verify_chain() is False


# ─────────────────────────── EXPORT ────────────────────────────────


def test_export_is_json_serializable():
    log = TransparencyLog()
    log.record("agent", "action", {"amount": 1})
    json.dumps(log.export())  # must not raise


def test_export_length_matches_log_length():
    log = TransparencyLog()
    for i in range(7):
        log.record("agent", f"step_{i}")
    assert len(log.export()) == 7


def test_export_contains_required_keys():
    log = TransparencyLog()
    log.record("agent", "action", {"k": "v"})
    record = log.export()[0]
    for key in ("index", "timestamp", "actor", "action", "payload", "prev_hash", "hash"):
        assert key in record


def test_export_empty_log_returns_empty_list():
    log = TransparencyLog()
    assert log.export() == []


def test_export_hash_matches_entry_hash():
    log = TransparencyLog()
    entry = log.record("agent", "action")
    exported = log.export()[0]
    assert exported["hash"] == entry.hash


# ─────────────────────────── EDGE CASES ────────────────────────────


def test_unicode_payload_values():
    log = TransparencyLog()
    log.record("agent", "action", {"name": "Ściśle Tajne 🔒", "lang": "日本語"})
    assert log.verify_chain() is True
    assert json.dumps(log.export())  # still serialisable


def test_nested_payload():
    log = TransparencyLog()
    log.record("agent", "complex_action", {"meta": {"nested": {"deep": [1, 2, 3]}}})
    assert log.verify_chain() is True
