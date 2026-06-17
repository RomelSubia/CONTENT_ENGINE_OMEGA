from __future__ import annotations

from .evidence import missing_required_fields, validate_preview_hash
from .models import HumanReviewRequest, HumanReviewResult
from .policy import APPROVAL_DECISION, decision_fail_reason
from .result import FAILED_CLOSED, PASS
from .state_machine import HumanReviewState, state_for_decision


def _failed(reason: str, request: HumanReviewRequest, missing: tuple[str, ...] = (), evidence_errors: tuple[str, ...] = ()) -> HumanReviewResult:
    return HumanReviewResult(
        status=FAILED_CLOSED,
        state=HumanReviewState.FAILED_CLOSED.value,
        decision=request.review_decision,
        approved_for_finalization_plan_only=False,
        finalization_allowed_now=False,
        queue_write_allowed_now=False,
        publishing_allowed_now=False,
        automation_allowed_now=False,
        runtime_execution_allowed_now=False,
        draft_creation_allowed_now=False,
        content_generation_allowed_now=False,
        fail_closed_reason=reason,
        missing_fields=missing,
        evidence_errors=evidence_errors,
    )


def validate_human_review(request: HumanReviewRequest) -> HumanReviewResult:
    missing = missing_required_fields(request)
    if missing:
        return _failed("missing_required_review_evidence", request, missing=missing)

    evidence_errors = validate_preview_hash(request)
    if evidence_errors:
        return _failed("invalid_or_tampered_review_evidence", request, evidence_errors=evidence_errors)

    decision_error = decision_fail_reason(request.review_decision)
    if decision_error:
        return _failed(decision_error, request)

    state = state_for_decision(request.review_decision or "")

    return HumanReviewResult(
        status=PASS,
        state=state.value,
        decision=request.review_decision,
        approved_for_finalization_plan_only=request.review_decision == APPROVAL_DECISION,
        finalization_allowed_now=False,
        queue_write_allowed_now=False,
        publishing_allowed_now=False,
        automation_allowed_now=False,
        runtime_execution_allowed_now=False,
        draft_creation_allowed_now=False,
        content_generation_allowed_now=False,
        fail_closed_reason=None,
        missing_fields=(),
        evidence_errors=(),
    )
