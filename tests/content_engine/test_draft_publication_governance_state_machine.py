from content_engine.content_draft_publication_governance.state_machine import (
    FAILED_CLOSED,
    READY_FOR_PUBLICATION_EXECUTION_GOVERNANCE_PLAN_ONLY,
    is_forbidden_state,
    validate_plan_only_path,
    validate_transition,
)


def test_state_machine_allows_plan_only_path():
    ok, errors = validate_plan_only_path()
    assert ok is True
    assert errors == ()


def test_state_machine_blocks_forbidden_terminal_states():
    assert is_forbidden_state("PUBLISHED") is True
    ok, error = validate_transition("PUBLICATION_INTENT_PREPARED", "PUBLISHED")
    assert ok is False
    assert error == "FORBIDDEN_PUBLICATION_GOVERNANCE_STATE"


def test_state_machine_rejects_illegal_transition():
    ok, error = validate_transition(FAILED_CLOSED, READY_FOR_PUBLICATION_EXECUTION_GOVERNANCE_PLAN_ONLY)
    assert ok is False
    assert error == "ILLEGAL_PUBLICATION_GOVERNANCE_TRANSITION"
