from __future__ import annotations

from .models import QueueWriteGovernanceRequest, QueueWriteGovernanceResult
from .policy import blocked_operation_flags


def serialize_audit_record(
    request: QueueWriteGovernanceRequest,
    result: QueueWriteGovernanceResult,
) -> dict[str, object]:
    return {
        "request_id": request.request_id,
        "component": "CONTENT_DRAFT_QUEUE_WRITE_GOVERNANCE_CORE",
        "decision": request.decision,
        "target_queue": request.target_queue,
        "queue_write_governance_status": result.queue_write_governance_status,
        "result_is_plan_only": result.result_is_plan_only,
        "blocked_operation_flags": blocked_operation_flags(),
        "result": result.as_dict(),
    }
