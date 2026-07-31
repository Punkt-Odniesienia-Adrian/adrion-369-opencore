"""
ADRION 369 Open-Core — Unity Module Test Suite
==============================================
31 tests covering: conflict detection, multiple conflicts, custom similarity,
non-string signatures, edge cases, record vs check semantics, large histories.
"""

from __future__ import annotations

import pytest

from adrion_opencore.unity import ConsistencyResult, UnityChecker


# ─────────────────────────── CONSISTENCY RESULT ─────────────────────


def test_consistency_result_consistent_true():
    r = ConsistencyResult(consistent=True, conflicting_with=[], reason="OK")
    assert r.consistent is True


def test_consistency_result_consistent_false():
    r = ConsistencyResult(consistent=False, conflicting_with=[0], reason="conflict")
    assert r.consistent is False


def test_consistency_result_stores_conflicting_indices():
    r = ConsistencyResult(consistent=False, conflicting_with=[0, 3, 7], reason="multi")
    assert r.conflicting_with == [0, 3, 7]


def test_consistency_result_stores_reason():
    r = ConsistencyResult(consistent=False, conflicting_with=[], reason="custom reason")
    assert r.reason == "custom reason"


# ─────────────────────────── BASIC BEHAVIOUR ────────────────────────


def test_no_conflict_on_first_decision():
    checker = UnityChecker()
    result = checker.check("input-A", "approve")
    assert result.consistent is True


def test_no_conflict_list_empty_on_first():
    checker = UnityChecker()
    result = checker.check("input-A", "approve")
    assert result.conflicting_with == []


def test_conflict_when_decision_contradicts_prior():
    checker = UnityChecker()
    checker.record("input-A", "approve")
    result = checker.check("input-A", "deny")
    assert result.consistent is False


def test_no_conflict_when_same_decision_repeats():
    checker = UnityChecker()
    checker.record("input-A", "approve")
    result = checker.check("input-A", "approve")
    assert result.consistent is True
    assert result.conflicting_with == []


def test_conflict_index_correct():
    checker = UnityChecker()
    checker.record("input-A", "approve")  # index 0
    result = checker.check("input-A", "deny")
    assert result.conflicting_with == [0]


def test_multiple_conflicts_reported():
    checker = UnityChecker()
    checker.record("input-A", "approve")   # index 0
    checker.record("input-B", "reject")    # index 1 – different input, no conflict
    checker.record("input-A", "approve")   # index 2 – same input, same decision
    # Now check opposite decision for input-A → conflicts with 0 and 2
    result = checker.check("input-A", "deny")
    assert result.consistent is False
    assert 0 in result.conflicting_with
    assert 2 in result.conflicting_with


def test_different_inputs_never_conflict():
    checker = UnityChecker()
    checker.record("input-A", "approve")
    result = checker.check("input-B", "deny")
    assert result.consistent is True


def test_check_does_not_record():
    checker = UnityChecker()
    checker.check("input-A", "approve")
    # If check had recorded, a second check with opposite decision would conflict
    result = checker.check("input-A", "deny")
    assert result.consistent is True  # no prior recording → no conflict


def test_record_then_multiple_checks_consistent():
    checker = UnityChecker()
    checker.record("input-A", "approve")
    for _ in range(5):
        result = checker.check("input-A", "approve")
        assert result.consistent is True


# ─────────────────────────── CONFLICT REASON ────────────────────────


def test_conflict_reason_mentions_count():
    checker = UnityChecker()
    checker.record("input-A", "approve")
    checker.record("input-A", "approve")
    result = checker.check("input-A", "deny")
    assert "2" in result.reason


def test_no_conflict_reason_indicates_no_conflicts():
    checker = UnityChecker()
    result = checker.check("input-A", "approve")
    assert "No conflicts" in result.reason


# ─────────────────────────── CUSTOM SIMILARITY ──────────────────────


def test_custom_similarity_fn_prefix_match():
    checker = UnityChecker(similarity_fn=lambda a, b: a[:3] == b[:3])
    checker.record("cat-food", "approve")
    result = checker.check("cat-litter", "deny")
    assert result.consistent is False


def test_custom_similarity_fn_never_similar():
    checker = UnityChecker(similarity_fn=lambda a, b: False)
    checker.record("input-A", "approve")
    result = checker.check("input-A", "deny")
    # similarity_fn always returns False → no match ever
    assert result.consistent is True


def test_custom_similarity_fn_always_similar():
    checker = UnityChecker(similarity_fn=lambda a, b: True)
    checker.record("input-A", "approve")
    result = checker.check("input-B", "deny")
    # every pair is "similar" → conflict
    assert result.consistent is False


def test_custom_similarity_fn_numeric_threshold():
    # Inputs within 10 of each other are "similar"
    checker = UnityChecker(similarity_fn=lambda a, b: abs(a - b) <= 10)
    checker.record(100, "approve")
    assert checker.check(105, "deny").consistent is False   # within threshold
    assert checker.check(115, "deny").consistent is True    # outside threshold


# ─────────────────────────── NON-STRING SIGNATURES ─────────────────


def test_integer_signatures():
    checker = UnityChecker()
    checker.record(42, "approve")
    assert checker.check(42, "deny").consistent is False
    assert checker.check(43, "deny").consistent is True


def test_tuple_signatures():
    checker = UnityChecker()
    checker.record(("user-1", "action-A"), "approve")
    result = checker.check(("user-1", "action-A"), "deny")
    assert result.consistent is False


def test_bool_decisions():
    checker = UnityChecker()
    checker.record("input", True)
    assert checker.check("input", False).consistent is False
    assert checker.check("input", True).consistent is True


def test_none_decision():
    checker = UnityChecker()
    checker.record("input", None)
    assert checker.check("input", None).consistent is True
    assert checker.check("input", "approve").consistent is False


# ─────────────────────────── LARGE HISTORY ──────────────────────────


def test_large_history_no_false_positives():
    checker = UnityChecker()
    for i in range(200):
        checker.record(f"input-{i}", "approve")
    # Completely new input → no conflict
    result = checker.check("input-NEW", "deny")
    assert result.consistent is True


def test_large_history_detects_conflict():
    checker = UnityChecker()
    for i in range(200):
        checker.record("shared-input", "approve")
    result = checker.check("shared-input", "deny")
    assert result.consistent is False
    assert len(result.conflicting_with) == 200


# ─────────────────────────── INDEPENDENCE ───────────────────────────


def test_independent_instances_no_shared_state():
    c1 = UnityChecker()
    c2 = UnityChecker()
    c1.record("input-A", "approve")
    result = c2.check("input-A", "deny")
    assert result.consistent is True  # c2 has no history


def test_fresh_instance_always_consistent():
    for _ in range(5):
        checker = UnityChecker()
        result = checker.check("any-input", "any-decision")
        assert result.consistent is True
