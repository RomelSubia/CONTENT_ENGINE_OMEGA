from __future__ import annotations

from .models import FAILED_STATUS, READY_STATUS, QueueWriteGovernanceResult


def build_plan_only_result(
    *,
    request_id: str,
    decision: str,
    errors: tuple[str, ...] = (),
) -> QueueWriteGovernanceResult:
    status = READY_STATUS if not errors else FAILED_STATUS
    return QueueWriteGovernanceResult(
        request_id=request_id,
        queue_write_governance_status=status,
        decision=decision,
        errors=errors,
        next_allowed_step_for_queue_write_execution_governance_only=not errors,
        result_is_plan_only=True,
        queue_write_performed=False,
        queue_item_created=False,
        queue_item_updated=False,
        target_queue_mutated=False,
        publishing_started=False,
        automation_started=False,
    )
