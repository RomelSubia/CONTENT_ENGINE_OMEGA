from __future__ import annotations

from .models import FinalizationDecision, FinalizationRequest, FinalizationStatus
from .policy import FinalizationPolicy
from .result import FinalizationResult
from .state_machine import FinalizationState, assert_transition
from .validator import validate_finalization_request


def build_finalization_record(request: FinalizationRequest) -> FinalizationResult:
    validate_finalization_request(request)

    state = FinalizationState.RECEIVED
    assert_transition(state, FinalizationState.EVIDENCE_VALIDATED)
    state = FinalizationState.EVIDENCE_VALIDATED

    assert_transition(state, FinalizationState.POLICY_VALIDATED)
    state = FinalizationState.POLICY_VALIDATED

    assert_transition(state, FinalizationState.RECORD_PREPARED)
    state = FinalizationState.RECORD_PREPARED

    assert_transition(state, FinalizationState.READY_FOR_QUEUE_GOVERNANCE_PLAN_ONLY)

    if request.decision == FinalizationDecision.FINALIZE_FOR_QUEUE_GOVERNANCE_PLAN_ONLY:
        status = FinalizationStatus.READY_FOR_QUEUE_GOVERNANCE_PLAN_ONLY
    elif request.decision == FinalizationDecision.REQUEST_REVISION_BEFORE_FINALIZATION:
        status = FinalizationStatus.REQUEST_REVISION_BEFORE_FINALIZATION
    elif request.decision == FinalizationDecision.REJECT_FINALIZATION:
        status = FinalizationStatus.REJECTED
    elif request.decision == FinalizationDecision.HOLD_FINALIZATION:
        status = FinalizationStatus.HOLD
    else:
        status = FinalizationStatus.ESCALATED

    return FinalizationResult(
        request_id=request.request_id,
        finalization_status=status.value,
        finalized_artifact_reference=f"finalization-ready://{request.request_id}",
        finalized_artifact_sha256=request.evidence.draft_sha256,
        queue_governance_readiness_reference=f"queue-governance-plan-only://{request.request_id}",
        next_allowed_step_for_queue_governance_only=True,
        blocked_operation_flags=FinalizationPolicy.blocked_operation_flags(),
    )
