from __future__ import annotations

from .models import PublicationGovernanceRequest, PublicationIntent


def build_plan_only_publication_intent(request: PublicationGovernanceRequest) -> PublicationIntent:
    return PublicationIntent(
        request_id=request.request_id,
        target_publication_channel=request.target_publication_channel,
        publication_intent=request.publication_intent,
        plan_only=True,
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
