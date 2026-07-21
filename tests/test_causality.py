from adrion_opencore.causality import CausalityTracker


def test_trace_records_steps():
    tracker = CausalityTracker()
    trace = tracker.start_trace("decision-1", "approve_transaction")
    trace.add_step("check_amount_threshold", {"amount": 100}, "under_threshold")
    trace.add_step("check_user_flags", {"user": "u1"}, "no_flags")
    assert len(trace.steps) == 2
    assert "approve_transaction" in trace.explain()


def test_get_trace_returns_none_for_unknown_id():
    tracker = CausalityTracker()
    assert tracker.get_trace("nonexistent") is None


def test_to_dict_roundtrip():
    tracker = CausalityTracker()
    trace = tracker.start_trace("d1", "deny_request")
    trace.add_step("privacy_check", {"field": "ssn"}, "blocked")
    d = trace.to_dict()
    assert d["decision"] == "deny_request"
    assert d["steps"][0]["output"] == "blocked"
