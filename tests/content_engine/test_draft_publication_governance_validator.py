from content_engine.content_draft_publication_governance.models import (
    READY_STATUS,
    REQUIRED_PUBLICATION_READINESS_MAP_STATUS,
    REQUIRED_QUEUE_WRITE_GOVERNANCE_STATUS,
    PublicationGovernanceEvidence,
    PublicationGovernanceRequest,
)
from content_engine.content_draft_publication_governance.validator import (
    validate_publication_governance_request,
)


VALID_HASH = "b" * 64


def request_with(**overrides):
    evidence = PublicationGovernanceEvidence(
        queue_write_governance_gate_close_reference="manifests/qwg-gate.json",
        queue_write_governance_gate_close_sha256=VALID_HASH,
        queue_write_governance_status=REQUIRED_QUEUE_WRITE_GOVERNANCE_STATUS,
        publication_readiness_map_reference="manifests/publication-map.json",
        publication_readiness_map_sha256=VALID_HASH,
        publication_readiness_map_status=REQUIRED_PUBLICATION_READINESS_MAP_STATUS,
        safe_preview_reference="reports/safe-preview.json",
        safe_preview_sha256=VALID_HASH,
        human_review_reference="reports/human-review.json",
        human_review_sha256=VALID_HASH,
        finalization_reference="reports/finalization.json",
        finalization_sha256=VALID_HASH,
    )
    data = {
        "request_id": "REQ-001",
        "operator_identity": "tester",
        "policy_version": "v1",
        "timestamp": "2026-06-18T00:00:00Z",
        "target_publication_channel": "plan-only-channel",
        "publication_intent": "prepare_publication_governance_plan_only",
        "idempotency_key": "idem-001",
        "decision": "AUTHORIZE_PUBLICATION_GOVERNANCE_PLAN_ONLY",
        "evidence": evidence,
    }
    data.update(overrides)
    return PublicationGovernanceRequest(**data)


def test_valid_request_returns_plan_only_ready():
    result = validate_publication_governance_request(request_with())
    assert result.publication_governance_status == READY_STATUS
    assert result.errors == ()
    assert result.result_is_plan_only is True
    assert result.publication_performed is False
    assert result.posting_performed is False
    assert result.publication_scheduled is False
    assert result.automation_started is False
    assert result.queue_write_performed is False


def test_missing_idempotency_key_fails_closed():
    result = validate_publication_governance_request(request_with(idempotency_key=""))
    assert result.publication_governance_status == "FAILED_CLOSED"
    assert "MISSING_IDEMPOTENCY_KEY" in result.errors
    assert result.publication_performed is False
    assert result.queue_write_performed is False
