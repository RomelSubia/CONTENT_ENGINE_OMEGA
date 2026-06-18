from __future__ import annotations

from dataclasses import asdict

from .models import COMPONENT, PublicationAuditRecord, PublicationGovernanceRequest, PublicationGovernanceResult
from .policy import blocked_operation_flags


def serialize_audit_record(
    request: PublicationGovernanceRequest,
    result: PublicationGovernanceResult,
) -> dict[str, object]:
    record = PublicationAuditRecord(
        component=COMPONENT,
        request_id=request.request_id,
        operator_identity=request.operator_identity,
        decision=request.decision,
        status=result.publication_governance_status,
        errors=result.errors,
        blocked_operation_flags=blocked_operation_flags(),
        metadata={
            "result_is_plan_only": result.result_is_plan_only,
            "publication_performed": result.publication_performed,
            "automation_started": result.automation_started,
            "queue_write_performed": result.queue_write_performed,
        },
    )
    return asdict(record)
