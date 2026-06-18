from content_engine.content_draft_publication_governance.policy import (
    FORBIDDEN_PUBLICATION_GOVERNANCE_DECISION,
    UNKNOWN_PUBLICATION_GOVERNANCE_DECISION,
    blocked_operation_flags,
    is_forbidden_operation,
    validate_decision,
)


def test_policy_accepts_only_plan_only_allowed_decision():
    ok, error = validate_decision("AUTHORIZE_PUBLICATION_GOVERNANCE_PLAN_ONLY")
    assert ok is True
    assert error is None


def test_policy_rejects_forbidden_publication_decisions():
    for decision in ["PUBLISH_NOW", "POST_NOW", "SCHEDULE_PUBLICATION_NOW", "TRIGGER_N8N_NOW"]:
        ok, error = validate_decision(decision)
        assert ok is False
        assert error == FORBIDDEN_PUBLICATION_GOVERNANCE_DECISION
        assert is_forbidden_operation(decision) is True


def test_policy_unknown_decision_fails_closed():
    ok, error = validate_decision("SOMETHING_ELSE")
    assert ok is False
    assert error == UNKNOWN_PUBLICATION_GOVERNANCE_DECISION


def test_blocked_operation_flags_are_all_false():
    flags = blocked_operation_flags()
    assert flags
    assert all(value is False for value in flags.values())
