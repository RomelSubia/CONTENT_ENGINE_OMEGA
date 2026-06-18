from __future__ import annotations

from .evidence import validate_evidence
from .models import QueueWriteGovernanceRequest, QueueWriteGovernanceResult
from .policy import validate_decision
from .write_intent import prepare_queue_write_intent
from .write_result import build_plan_only_result


def validate_queue_write_governance_request(
    request: QueueWriteGovernanceRequest,
) -> QueueWriteGovernanceResult:
    errors: list[str] = []

    for field_name in ("request_id", "operator_identity", "policy_version", "timestamp"):
        if not getattr(request, field_name):
            errors.append(f"MISSING_{field_name.upper()}")

    if not request.idempotency_key:
        errors.append("MISSING_IDEMPOTENCY_KEY")

    if not request.target_queue:
        errors.append("MISSING_TARGET_QUEUE")

    if not request.write_intent:
        errors.append("MISSING_WRITE_INTENT")

    evidence_errors = validate_evidence(request.evidence)
    errors.extend(evidence_errors)

    decision_ok, decision_error = validate_decision(request.decision)
    if not decision_ok and decision_error:
        errors.append(decision_error)

    if not errors:
        intent = prepare_queue_write_intent(request)
        if (
            intent.queue_write_performed
            or intent.queue_item_created
            or intent.queue_item_updated
            or intent.target_queue_mutated
        ):
            errors.append("QUEUE_WRITE_INTENT_SIDE_EFFECT_DETECTED")

    return build_plan_only_result(
        request_id=request.request_id,
        decision=request.decision,
        errors=tuple(errors),
    )
