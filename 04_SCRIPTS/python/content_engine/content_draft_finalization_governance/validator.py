from __future__ import annotations

from .evidence import validate_evidence
from .models import FinalizationRequest
from .policy import FinalizationPolicy


def validate_finalization_request(request: FinalizationRequest) -> None:
    required_values = {
        "request_id": request.request_id,
        "operator_identity": request.operator_identity,
        "policy_version": request.policy_version,
        "timestamp": request.timestamp,
        "intent": request.intent,
    }

    missing = [key for key, value in required_values.items() if not value]
    if missing:
        raise ValueError(f"MISSING_FINALIZATION_REQUEST_FIELDS: {missing}")

    validate_evidence(request.evidence)
    FinalizationPolicy.assert_allowed_decision(request.decision)
