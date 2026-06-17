from __future__ import annotations

from enum import Enum


class FinalizationState(str, Enum):
    RECEIVED = "RECEIVED"
    EVIDENCE_VALIDATED = "EVIDENCE_VALIDATED"
    POLICY_VALIDATED = "POLICY_VALIDATED"
    RECORD_PREPARED = "RECORD_PREPARED"
    READY_FOR_QUEUE_GOVERNANCE_PLAN_ONLY = "READY_FOR_QUEUE_GOVERNANCE_PLAN_ONLY"
    FAILED_CLOSED = "FAILED_CLOSED"


_ALLOWED_TRANSITIONS = {
    FinalizationState.RECEIVED: {FinalizationState.EVIDENCE_VALIDATED, FinalizationState.FAILED_CLOSED},
    FinalizationState.EVIDENCE_VALIDATED: {FinalizationState.POLICY_VALIDATED, FinalizationState.FAILED_CLOSED},
    FinalizationState.POLICY_VALIDATED: {FinalizationState.RECORD_PREPARED, FinalizationState.FAILED_CLOSED},
    FinalizationState.RECORD_PREPARED: {FinalizationState.READY_FOR_QUEUE_GOVERNANCE_PLAN_ONLY, FinalizationState.FAILED_CLOSED},
    FinalizationState.READY_FOR_QUEUE_GOVERNANCE_PLAN_ONLY: set(),
    FinalizationState.FAILED_CLOSED: set(),
}


def can_transition(source: FinalizationState, target: FinalizationState) -> bool:
    return target in _ALLOWED_TRANSITIONS[source]


def assert_transition(source: FinalizationState, target: FinalizationState) -> None:
    if not can_transition(source, target):
        raise ValueError(f"INVALID_FINALIZATION_TRANSITION: {source} -> {target}")
