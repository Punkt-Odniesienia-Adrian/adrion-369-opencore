"""
ADRION 369 Open-Core — Causality Module Test Suite
===================================================
29 tests covering: trace creation, step recording, explain format,
to_dict contract, multiple trackers, edge cases, output type variety.
"""

from __future__ import annotations

import pytest

from adrion_opencore.causality import CausalTrace, CausalityTracker, ReasoningStep


# ─────────────────────────── REASONING STEP ─────────────────────────


def test_reasoning_step_stores_fields():
    step = ReasoningStep(
        description="check_threshold",
        inputs={"amount": 100},
        output="under_threshold",
    )
    assert step.description == "check_threshold"
    assert step.inputs == {"amount": 100}
    assert step.output == "under_threshold"


def test_reasoning_step_bool_output():
    step = ReasoningStep("privacy_check", {"field": "ssn"}, False)
    assert step.output is False


def test_reasoning_step_none_output():
    step = ReasoningStep("no_op", {}, None)
    assert step.output is None


def test_reasoning_step_list_output():
    step = ReasoningStep("extract_features", {"text": "hello"}, ["token_1", "token_2"])
    assert isinstance(step.output, list)


# ─────────────────────────── CAUSAL TRACE ───────────────────────────


def test_new_trace_has_no_steps():
    trace = CausalTrace(decision="approve")
    assert trace.steps == []


def test_add_step_increases_count():
    trace = CausalTrace(decision="approve")
    trace.add_step("step_1", {}, "ok")
    trace.add_step("step_2", {}, "ok")
    assert len(trace.steps) == 2


def test_add_step_preserves_order():
    trace = CausalTrace(decision="approve")
    trace.add_step("alpha", {}, 1)
    trace.add_step("beta", {}, 2)
    assert trace.steps[0].description == "alpha"
    assert trace.steps[1].description == "beta"


def test_explain_contains_decision():
    trace = CausalTrace(decision="deny_access")
    assert "deny_access" in trace.explain()


def test_explain_contains_all_step_descriptions():
    trace = CausalTrace(decision="approve")
    trace.add_step("check_amount", {"amount": 10}, "ok")
    trace.add_step("check_flags", {"user": "u1"}, "clean")
    explanation = trace.explain()
    assert "check_amount" in explanation
    assert "check_flags" in explanation


def test_explain_contains_step_outputs():
    trace = CausalTrace(decision="approve")
    trace.add_step("guardians_vote", {}, "unanimous")
    assert "unanimous" in trace.explain()


def test_explain_empty_trace():
    trace = CausalTrace(decision="no_op")
    result = trace.explain()
    assert "no_op" in result
    # Just the decision line, no steps
    assert result.count("\n") == 0


def test_explain_step_numbers_start_at_one():
    trace = CausalTrace(decision="approve")
    trace.add_step("step_a", {}, "x")
    assert "1." in trace.explain()


def test_to_dict_has_decision_key():
    trace = CausalTrace(decision="approve")
    d = trace.to_dict()
    assert d["decision"] == "approve"


def test_to_dict_has_steps_key():
    trace = CausalTrace(decision="approve")
    d = trace.to_dict()
    assert "steps" in d


def test_to_dict_steps_is_list():
    trace = CausalTrace(decision="approve")
    trace.add_step("check", {}, "ok")
    assert isinstance(trace.to_dict()["steps"], list)


def test_to_dict_step_structure():
    trace = CausalTrace(decision="deny")
    trace.add_step("privacy_check", {"field": "ssn"}, "blocked")
    step_dict = trace.to_dict()["steps"][0]
    assert step_dict["description"] == "privacy_check"
    assert step_dict["inputs"] == {"field": "ssn"}
    assert step_dict["output"] == "blocked"


def test_to_dict_empty_trace_steps():
    trace = CausalTrace(decision="no_op")
    assert trace.to_dict()["steps"] == []


def test_to_dict_multiple_steps_count():
    trace = CausalTrace(decision="complex")
    for i in range(5):
        trace.add_step(f"step_{i}", {"i": i}, i * 2)
    assert len(trace.to_dict()["steps"]) == 5


def test_add_step_with_nested_inputs():
    trace = CausalTrace(decision="approve")
    trace.add_step("nested_check", {"meta": {"level": 3, "tags": ["a", "b"]}}, True)
    assert trace.steps[0].inputs["meta"]["level"] == 3


def test_add_step_unicode_description():
    trace = CausalTrace(decision="Zatwierdzono")
    trace.add_step("Weryfikacja tożsamości 🔐", {"user": "u1"}, "OK")
    assert "Weryfikacja" in trace.explain()


# ─────────────────────────── CAUSALITY TRACKER ──────────────────────


def test_tracker_start_trace_returns_trace():
    tracker = CausalityTracker()
    trace = tracker.start_trace("d-001", "approve")
    assert isinstance(trace, CausalTrace)


def test_tracker_get_trace_returns_stored():
    tracker = CausalityTracker()
    tracker.start_trace("d-001", "approve")
    result = tracker.get_trace("d-001")
    assert result is not None
    assert result.decision == "approve"


def test_tracker_get_trace_returns_none_for_unknown():
    tracker = CausalityTracker()
    assert tracker.get_trace("nonexistent") is None


def test_tracker_multiple_traces_independent():
    tracker = CausalityTracker()
    t1 = tracker.start_trace("d-001", "approve")
    t2 = tracker.start_trace("d-002", "deny")
    t1.add_step("step", {}, "ok")
    assert len(t2.steps) == 0


def test_tracker_overwrite_trace_id():
    tracker = CausalityTracker()
    tracker.start_trace("d-001", "approve")
    tracker.start_trace("d-001", "deny")  # overwrite
    assert tracker.get_trace("d-001").decision == "deny"


def test_tracker_steps_added_via_returned_trace():
    tracker = CausalityTracker()
    trace = tracker.start_trace("d-001", "approve")
    trace.add_step("g1_check", {}, "pass")
    retrieved = tracker.get_trace("d-001")
    assert len(retrieved.steps) == 1


def test_independent_trackers_do_not_share_state():
    t1 = CausalityTracker()
    t2 = CausalityTracker()
    t1.start_trace("d-001", "approve")
    assert t2.get_trace("d-001") is None


def test_tracker_ten_traces():
    tracker = CausalityTracker()
    for i in range(10):
        tracker.start_trace(f"d-{i:03}", f"decision_{i}")
    for i in range(10):
        assert tracker.get_trace(f"d-{i:03}") is not None
