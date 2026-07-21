from adrion_opencore.unity import UnityChecker


def test_no_conflict_on_first_decision():
    checker = UnityChecker()
    result = checker.check("input-signature-A", "approve")
    assert result.consistent is True


def test_conflict_detected_on_contradiction():
    checker = UnityChecker()
    checker.record("input-signature-A", "approve")
    result = checker.check("input-signature-A", "deny")
    assert result.consistent is False
    assert result.conflicting_with == [0]


def test_no_conflict_when_decision_repeats():
    checker = UnityChecker()
    checker.record("input-signature-A", "approve")
    result = checker.check("input-signature-A", "approve")
    assert result.consistent is True


def test_custom_similarity_function():
    checker = UnityChecker(similarity_fn=lambda a, b: a[:3] == b[:3])
    checker.record("cat-food", "approve")
    result = checker.check("cat-litter", "deny")
    assert result.consistent is False
