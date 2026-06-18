from __future__ import annotations

from typing import Any

from .evidence import validate_queue_governance_evidence
from .models import QueueGovernanceRequest
from .policy import validate_queue_governance_policy


class QueueGovernanceValidationError(ValueError):
    pass


REQUIRED_REQUEST_FIELDS = [
    "request_id",
    "operator_identity",
    "policy_version",
    "timestamp",
    "intent",
    "evidence",
    "decision",
]


def _get_value(request: Any, name: str) -> Any:
    if isinstance(request, dict):
        return request.get(name)
    return getattr(request, name, None)


def validate_queue_governance_request(request: QueueGovernanceRequest | dict[str, Any]) -> QueueGovernanceRequest | dict[str, Any]:
    missing = [
        name
        for name in REQUIRED_REQUEST_FIELDS
        if _get_value(request, name) in (None, "")
    ]
    if missing:
        raise QueueGovernanceValidationError("MISSING_QUEUE_GOVERNANCE_REQUEST_FIELDS")

    try:
        validate_queue_governance_evidence(_get_value(request, "evidence"))
        validate_queue_governance_policy(_get_value(request, "decision"))
    except ValueError as exc:
        raise QueueGovernanceValidationError(str(exc)) from exc

    return request
