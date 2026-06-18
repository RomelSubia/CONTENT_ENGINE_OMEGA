from __future__ import annotations

from .models import QueueWriteGovernanceRequest, QueueWriteIntent


def prepare_queue_write_intent(request: QueueWriteGovernanceRequest) -> QueueWriteIntent:
    return QueueWriteIntent(
        target_queue=request.target_queue,
        write_intent=request.write_intent,
        idempotency_key=request.idempotency_key,
        result_is_plan_only=True,
        queue_write_performed=False,
        queue_item_created=False,
        queue_item_updated=False,
        target_queue_mutated=False,
    )
