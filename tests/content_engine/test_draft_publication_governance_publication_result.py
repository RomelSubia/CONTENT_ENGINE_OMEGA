from content_engine.content_draft_publication_governance.models import (
    READY_STATUS,
    REQUIRED_PUBLICATION_READINESS_MAP_STATUS,
    REQUIRED_QUEUE_WRITE_GOVERNANCE_STATUS,
    PublicationGovernanceEvidence,
    PublicationGovernanceRequest,
)
from content_engine.content_draft_publication_governance.publication_result import build_plan_only_result


def make_request():
    h = "d" * 64
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
    return PublicationGovernanceRequest(
        request_id="REQ-RESULT",
        operator_identity="tester",
        policy_version="v1",
        timestamp="2026-06-18T00:00:00Z",
        target_publication_channel="channel-a",
        publication_intent="prepare_publication_governance_plan_only",
        idempotency_key="idem-result",
        decision="AUTHORIZE_PUBLICATION_GOVERNANCE_PLAN_ONLY",
        evidence=evidence,
    )


def test_plan_only_result_ready_has_no_side_effects():
    result = build_plan_only_result(make_request(), status=READY_STATUS)
    assert result.publication_governance_status == READY_STATUS
    assert result.result_is_plan_only is True
    assert result.publication_performed is False
    assert result.posting_performed is False
    assert result.publication_scheduled is False
    assert result.automation_started is False
    assert result.queue_item_created is False


def test_plan_only_result_with_errors_fails_closed():
    result = build_plan_only_result(make_request(), errors=("X",))
    assert result.publication_governance_status == "FAILED_CLOSED"
    assert result.errors == ("X",)
    assert result.publication_performed is False
