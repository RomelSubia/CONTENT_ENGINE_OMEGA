from __future__ import annotations

from .models import FAILED_STATUS, READY_STATUS, PublicationGovernanceRequest, PublicationGovernanceResult


def build_plan_only_result(
    request: PublicationGovernanceRequest,
    *,
    errors: tuple[str, ...] = (),
    status: str | None = None,
) -> PublicationGovernanceResult:
    final_status = status or (READY_STATUS if not errors else FAILED_STATUS)
    return PublicationGovernanceResult(
        request_id=request.request_id,
        publication_governance_status=final_status,
        errors=tuple(errors),
        result_is_plan_only=True,
        publication_performed=False,
        posting_performed=False,
        publication_scheduled=False,
        publication_channel_mutated=False,
        automation_started=False,
        n8n_started=False,
        webhook_started=False,
        capa9_started=False,
        queue_write_performed=False,
        queue_item_created=False,
        queue_item_updated=False,
        runtime_execution_started=False,
    )
