from __future__ import annotations

from .models import FAILED_STATUS, READY_STATUS

RECEIVED = "RECEIVED"
EVIDENCE_VALIDATED = "QUEUE_GOVERNANCE_EVIDENCE_VALIDATED"
POLICY_VALIDATED = "QUEUE_WRITE_POLICY_VALIDATED"
INTENT_PREPARED = "QUEUE_WRITE_INTENT_PREPARED"

ALLOWED_TRANSITIONS = frozenset({
    (RECEIVED, EVIDENCE_VALIDATED),
    (EVIDENCE_VALIDATED, POLICY_VALIDATED),
    (POLICY_VALIDATED, INTENT_PREPARED),
    (INTENT_PREPARED, READY_STATUS),
})

FORBIDDEN_STATES = frozenset({
    "QUEUE_WRITTEN",
    "QUEUE_ITEM_CREATED",
    "QUEUE_ITEM_UPDATED",
    "PUBLISHED",
    "AUTOMATED",
})


def validate_transition(current_state: str, next_state: str) -> tuple[bool, str | None]:
    if next_state in FORBIDDEN_STATES:
        return False, "FORBIDDEN_PRODUCTIVE_STATE"
    if (current_state, next_state) not in ALLOWED_TRANSITIONS:
        return False, "INVALID_QUEUE_WRITE_GOVERNANCE_TRANSITION"
    return True, None


def fail_closed_state() -> str:
    return FAILED_STATUS
