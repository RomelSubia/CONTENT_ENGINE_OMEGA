from __future__ import annotations

from .evidence import validate_evidence
from .models import FAILED_STATUS, READY_STATUS, PublicationGovernanceRequest, PublicationGovernanceResult
from .policy import validate_decision
from .publication_intent import build_plan_only_publication_intent
from .publication_result import build_plan_only_result
from .state_machine import validate_plan_only_path


def validate_publication_governance_request(
    request: PublicationGovernanceRequest,
) -> PublicationGovernanceResult:
    errors: list[str] = []

    required_request_fields = {
        "request_id": request.request_id,
        "operator_identity": request.operator_identity,
        "policy_version": request.policy_version,
        "timestamp": request.timestamp,
        "target_publication_channel": request.target_publication_channel,
        "publication_intent": request.publication_intent,
        "idempotency_key": request.idempotency_key,
    }

    for field_name, value in required_request_fields.items():
        if not value:
            errors.append(f"MISSING_{field_name.upper()}")

    evidence_ok, evidence_errors = validate_evidence(request.evidence)
    if not evidence_ok:
        errors.extend(evidence_errors)

    decision_ok, decision_error = validate_decision(request.decision)
    if not decision_ok and decision_error:
        errors.append(decision_error)

    state_ok, state_errors = validate_plan_only_path()
    if not state_ok:
        errors.extend(state_errors)

    if errors:
        return build_plan_only_result(
            request,
            errors=tuple(errors),
            status=FAILED_STATUS,
        )

    intent = build_plan_only_publication_intent(request)
    if not intent.plan_only:
        return build_plan_only_result(
            request,
            errors=("PUBLICATION_INTENT_NOT_PLAN_ONLY",),
            status=FAILED_STATUS,
        )

    return build_plan_only_result(
        request,
        errors=(),
        status=READY_STATUS,
    )
