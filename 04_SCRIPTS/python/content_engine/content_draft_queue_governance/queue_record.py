from __future__ import annotations

import hashlib
import json
from typing import Any

from .models import QueueGovernanceDecision, QueueGovernanceRequest, QueueGovernanceStatus
from .policy import blocked_operation_flags
from .result import QueueGovernanceResult
from .state_machine import QueueGovernanceState, transition_queue_governance_state
from .validator import validate_queue_governance_request


def _request_id(request: QueueGovernanceRequest | dict[str, Any]) -> str:
    if isinstance(request, dict):
        return str(request["request_id"])
    return str(request.request_id)


def _decision(request: QueueGovernanceRequest | dict[str, Any]) -> str:
    decision = request["decision"] if isinstance(request, dict) else request.decision
    return decision.value if isinstance(decision, QueueGovernanceDecision) else str(decision)


def _result_status_for_decision(decision: str) -> QueueGovernanceStatus:
    mapping = {
        QueueGovernanceDecision.PREPARE_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY.value: QueueGovernanceStatus.READY_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY,
        QueueGovernanceDecision.REQUEST_REVISION_BEFORE_QUEUE.value: QueueGovernanceStatus.REQUEST_REVISION_BEFORE_QUEUE,
        QueueGovernanceDecision.REJECT_QUEUE_READINESS.value: QueueGovernanceStatus.REJECTED,
        QueueGovernanceDecision.HOLD_QUEUE_READINESS.value: QueueGovernanceStatus.HOLD,
        QueueGovernanceDecision.ESCALATE_QUEUE_REVIEW.value: QueueGovernanceStatus.ESCALATED,
    }
    return mapping[decision]


def _canonical_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def build_queue_governance_record(request: QueueGovernanceRequest | dict[str, Any]) -> QueueGovernanceResult:
    validate_queue_governance_request(request)

    current = QueueGovernanceState.RECEIVED
    current = transition_queue_governance_state(current, QueueGovernanceState.FINALIZATION_EVIDENCE_VALIDATED)
    current = transition_queue_governance_state(current, QueueGovernanceState.QUEUE_POLICY_VALIDATED)
    current = transition_queue_governance_state(current, QueueGovernanceState.QUEUE_RECORD_PREPARED)
    current = transition_queue_governance_state(current, QueueGovernanceState.READY_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY)

    request_id = _request_id(request)
    status = _result_status_for_decision(_decision(request))
    record_reference = f"queue-governance-ready://{request_id}"
    readiness_reference = f"queue-write-governance-plan-only://{request_id}"
    blocked_flags = blocked_operation_flags()

    material = _canonical_payload({
        "request_id": request_id,
        "queue_governance_status": status.value,
        "queue_governance_record_reference": record_reference,
        "queue_write_readiness_reference": readiness_reference,
        "state": current.value,
        "blocked_operation_flags": blocked_flags,
    })
    record_sha256 = hashlib.sha256(material.encode("utf-8")).hexdigest()

    result = QueueGovernanceResult(
        request_id=request_id,
        queue_governance_status=status,
        queue_governance_record_reference=record_reference,
        queue_governance_record_sha256=record_sha256,
        queue_write_readiness_reference=readiness_reference,
        next_allowed_step_for_queue_write_governance_only=True,
        blocked_operation_flags=blocked_flags,
    )
    result.assert_no_productive_side_effects()
    return result
