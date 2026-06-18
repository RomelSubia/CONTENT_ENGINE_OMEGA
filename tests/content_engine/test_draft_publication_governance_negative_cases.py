from content_engine.content_draft_publication_governance.models import (
    REQUIRED_PUBLICATION_READINESS_MAP_STATUS,
    REQUIRED_QUEUE_WRITE_GOVERNANCE_STATUS,
    PublicationGovernanceEvidence,
    PublicationGovernanceRequest,
)
from content_engine.content_draft_publication_governance.validator import (
    validate_publication_governance_request,
)


VALID_HASH = "e" * 64


def request_with_decision(decision: str):
    evidence = PublicationGovernanceEvidence(
        queue_write_governance_gate_close_reference="qwg.json",
        queue_write_governance_gate_close_sha256=VALID_HASH,
        queue_write_governance_status=REQUIRED_QUEUE_WRITE_GOVERNANCE_STATUS,
        publication_readiness_map_reference="map.json",
        publication_readiness_map_sha256=VALID_HASH,
        publication_readiness_map_status=REQUIRED_PUBLICATION_READINESS_MAP_STATUS,
        safe_preview_reference="preview.json",
        safe_preview_sha256=VALID_HASH,
        human_review_reference="review.json",
        human_review_sha256=VALID_HASH,
        finalization_reference="final.json",
        finalization_sha256=VALID_HASH,
    )
    return PublicationGovernanceRequest(
        request_id=f"REQ-{decision}",
        operator_identity="tester",
        policy_version="v1",
        timestamp="2026-06-18T00:00:00Z",
        target_publication_channel="channel-a",
        publication_intent="prepare_publication_governance_plan_only",
        idempotency_key=f"idem-{decision}",
        decision=decision,
        evidence=evidence,
    )


def test_productive_decisions_fail_closed():
    forbidden = [
        "PUBLISH_NOW",
        "POST_NOW",
        "SCHEDULE_PUBLICATION_NOW",
        "UPDATE_PUBLICATION_CHANNEL_NOW",
        "TRIGGER_N8N_NOW",
        "TRIGGER_WEBHOOK_NOW",
        "TRIGGER_CAPA9_NOW",
        "AUTOMATE_NOW",
        "WRITE_QUEUE_NOW",
        "CREATE_QUEUE_ITEM_NOW",
        "UPDATE_QUEUE_ITEM_NOW",
        "GENERATE_CONTENT_NOW",
        "FINALIZE_CONTENT_NOW",
        "BUILD_ARGOS_BRIDGE_NOW",
    ]
    for decision in forbidden:
        result = validate_publication_governance_request(request_with_decision(decision))
        assert result.publication_governance_status == "FAILED_CLOSED"
        assert "FORBIDDEN_PUBLICATION_GOVERNANCE_DECISION" in result.errors
        assert result.publication_performed is False
        assert result.posting_performed is False
        assert result.publication_scheduled is False
        assert result.automation_started is False
        assert result.n8n_started is False
        assert result.webhook_started is False
        assert result.capa9_started is False
        assert result.queue_write_performed is False
        assert result.queue_item_created is False
        assert result.queue_item_updated is False
