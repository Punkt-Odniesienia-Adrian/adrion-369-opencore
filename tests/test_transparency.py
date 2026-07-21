from adrion_opencore.transparency import TransparencyLog


def test_empty_log_verifies():
    log = TransparencyLog()
    assert log.verify_chain() is True
    assert len(log) == 0


def test_record_and_verify():
    log = TransparencyLog()
    log.record("agent-1", "approve_transaction", {"amount": 100})
    log.record("agent-1", "log_decision", {"reason": "within policy"})
    assert len(log) == 2
    assert log.verify_chain() is True


def test_tamper_detection():
    log = TransparencyLog()
    entry = log.record("agent-1", "approve_transaction", {"amount": 100})
    entry.payload["amount"] = 999999  # tamper after the fact
    assert log.verify_chain() is False


def test_export_is_json_serializable():
    import json
    log = TransparencyLog()
    log.record("agent-1", "approve_transaction", {"amount": 100})
    json.dumps(log.export())
