from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.content_draft_queue_write_governance.models import (
    REQUIRED_UPSTREAM_STATUS,
    QueueWriteGovernanceEvidence,
    QueueWriteGovernanceRequest,
)


VALID_HASH = "a" * 64


def valid_evidence() -> QueueWriteGovernanceEvidence:
    return QueueWriteGovernanceEvidence(
        queue_governance_reference="reports/queue-governance.json",
        queue_governance_sha256=VALID_HASH,
        queue_governance_status=REQUIRED_UPSTREAM_STATUS,
        queue_governance_manifest_reference="manifests/queue-governance.json",
        source_draft_reference="drafts/source.json",
        source_draft_sha256=VALID_HASH,
        finalization_reference="finalization/final.json",
        finalization_sha256=VALID_HASH,
    )


def valid_request(**overrides) -> QueueWriteGovernanceRequest:
    data = {
        "request_id": "REQ-001",
        "operator_identity": "test-operator",
        "policy_version": "v1",
        "timestamp": "2026-06-18T00:00:00Z",
        "target_queue": "draft_queue",
        "write_intent": "prepare_plan_only_queue_write",
        "idempotency_key": "idem-001",
        "decision": "AUTHORIZE_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY",
        "evidence": valid_evidence(),
    }
    data.update(overrides)
    return QueueWriteGovernanceRequest(**data)

from content_engine.content_draft_queue_write_governance.validator import (
    validate_queue_write_governance_request,
)


def test_valid_request_returns_plan_only_ready_result():
    result = validate_queue_write_governance_request(valid_request())
    assert result.queue_write_governance_status == "READY_FOR_QUEUE_WRITE_EXECUTION_GOVERNANCE_PLAN_ONLY"
    assert result.next_allowed_step_for_queue_write_execution_governance_only is True
    assert result.result_is_plan_only is True
    assert result.queue_write_performed is False
    assert result.queue_item_created is False
    assert result.queue_item_updated is False


def test_missing_idempotency_fails_closed():
    result = validate_queue_write_governance_request(valid_request(idempotency_key=""))
    assert result.queue_write_governance_status == "FAILED_CLOSED"
    assert "MISSING_IDEMPOTENCY_KEY" in result.errors


def test_forbidden_decision_fails_closed():
    result = validate_queue_write_governance_request(valid_request(decision="WRITE_QUEUE_NOW"))
    assert result.queue_write_governance_status == "FAILED_CLOSED"
    assert "FORBIDDEN_QUEUE_WRITE_GOVERNANCE_DECISION" in result.errors
    assert result.queue_write_performed is False
