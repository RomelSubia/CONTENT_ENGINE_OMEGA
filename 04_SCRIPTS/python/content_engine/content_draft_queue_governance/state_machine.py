from __future__ import annotations

from enum import Enum


class QueueGovernanceState(str, Enum):
    RECEIVED = "RECEIVED"
    FINALIZATION_EVIDENCE_VALIDATED = "FINALIZATION_EVIDENCE_VALIDATED"
    QUEUE_POLICY_VALIDATED = "QUEUE_POLICY_VALIDATED"
    QUEUE_RECORD_PREPARED = "QUEUE_RECORD_PREPARED"
    READY_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY = "READY_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY"
    FAILED_CLOSED = "FAILED_CLOSED"


class QueueGovernanceStateMachineError(ValueError):
    pass


ALLOWED_TRANSITIONS = {
    (QueueGovernanceState.RECEIVED, QueueGovernanceState.FINALIZATION_EVIDENCE_VALIDATED),
    (QueueGovernanceState.FINALIZATION_EVIDENCE_VALIDATED, QueueGovernanceState.QUEUE_POLICY_VALIDATED),
    (QueueGovernanceState.QUEUE_POLICY_VALIDATED, QueueGovernanceState.QUEUE_RECORD_PREPARED),
    (QueueGovernanceState.QUEUE_RECORD_PREPARED, QueueGovernanceState.READY_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY),
}


def normalize_state(state: QueueGovernanceState | str) -> QueueGovernanceState:
    try:
        return state if isinstance(state, QueueGovernanceState) else QueueGovernanceState(str(state))
    except ValueError as exc:
        raise QueueGovernanceStateMachineError("INVALID_QUEUE_GOVERNANCE_TRANSITION") from exc


def transition_queue_governance_state(
    current: QueueGovernanceState | str,
    next_state: QueueGovernanceState | str,
) -> QueueGovernanceState:
    normalized_current = normalize_state(current)
    normalized_next = normalize_state(next_state)
    if (normalized_current, normalized_next) not in ALLOWED_TRANSITIONS:
        raise QueueGovernanceStateMachineError("INVALID_QUEUE_GOVERNANCE_TRANSITION")
    return normalized_next
