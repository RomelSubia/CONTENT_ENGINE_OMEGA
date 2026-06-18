from content_engine.content_draft_publication_governance.models import (
    REQUIRED_PUBLICATION_READINESS_MAP_STATUS,
    REQUIRED_QUEUE_WRITE_GOVERNANCE_STATUS,
    PublicationGovernanceEvidence,
    PublicationGovernanceRequest,
)
from content_engine.content_draft_publication_governance.publication_intent import (
    build_plan_only_publication_intent,
)


def test_publication_intent_is_plan_only_and_non_mutating():
    h = "c" * 64
    evidence = PublicationGovernanceEvidence(
        queue_write_governance_gate_close_reference="qwg.json",
        queue_write_governance_gate_close_sha256=h,
        queue_write_governance_status=REQUIRED_QUEUE_WRITE_GOVERNANCE_STATUS,
        publication_readiness_map_reference="map.json",
        publication_readiness_map_sha256=h,
        publication_readiness_map_status=REQUIRED_PUBLICATION_READINESS_MAP_STATUS,
        safe_preview_reference="preview.json",
        safe_preview_sha256=h,
        human_review_reference="review.json",
        human_review_sha256=h,
        finalization_reference="final.json",
        finalization_sha256=h,
    )
    request = PublicationGovernanceRequest(
        request_id="REQ-INTENT",
        operator_identity="tester",
        policy_version="v1",
        timestamp="2026-06-18T00:00:00Z",
        target_publication_channel="channel-a",
        publication_intent="prepare_publication_governance_plan_only",
        idempotency_key="idem-intent",
        decision="AUTHORIZE_PUBLICATION_GOVERNANCE_PLAN_ONLY",
        evidence=evidence,
    )
    intent = build_plan_only_publication_intent(request)
    assert intent.plan_only is True
    assert intent.publication_performed is False
    assert intent.posting_performed is False
    assert intent.publication_scheduled is False
    assert intent.publication_channel_mutated is False
    assert intent.n8n_started is False
    assert intent.queue_write_performed is False
