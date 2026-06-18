from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

HASH = "a" * 64


def evidence_kwargs():
    return {
        "finalization_result_reference": "finalization-ready://req-1",
        "finalization_result_sha256": HASH,
        "finalization_manifest_reference": "manifest://finalization",
        "draft_reference": "draft://req-1",
        "draft_sha256": HASH,
        "human_review_reference": "human-review://req-1",
        "human_review_sha256": HASH,
        "safe_preview_reference": "safe-preview://req-1",
        "safe_preview_sha256": HASH,
    }


def request_kwargs():
    return {
        "request_id": "req-1",
        "operator_identity": "tester",
        "policy_version": "v1",
        "timestamp": "2026-01-01T00:00:00Z",
        "intent": "prepare queue governance plan only",
    }

from content_engine.content_draft_queue_governance.models import (
    QueueGovernanceDecision,
    QueueGovernanceEvidence,
    QueueGovernanceRequest,
    QueueGovernanceStatus,
)
from content_engine.content_draft_queue_governance.queue_record import build_queue_governance_record
from content_engine.content_draft_queue_governance.validator import (
    QueueGovernanceValidationError,
    validate_queue_governance_request,
)


def make_request(decision=QueueGovernanceDecision.PREPARE_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY):
    return QueueGovernanceRequest(
        **request_kwargs(),
        evidence=QueueGovernanceEvidence(**evidence_kwargs()),
        decision=decision,
    )


def test_validator_accepts_valid_request():
    request = make_request()
    assert validate_queue_governance_request(request) == request


def test_queue_record_builds_plan_only_result():
    result = build_queue_governance_record(make_request())
    assert result.request_id == "req-1"
    assert result.queue_governance_status is QueueGovernanceStatus.READY_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY
    assert result.queue_governance_record_reference == "queue-governance-ready://req-1"
    assert result.queue_write_readiness_reference == "queue-write-governance-plan-only://req-1"
    assert result.next_allowed_step_for_queue_write_governance_only is True
    assert result.blocked_operation_flags["queue_write_performed"] is False
    assert result.blocked_operation_flags["queue_item_created"] is False
    assert result.blocked_operation_flags["publishing_started"] is False


def test_validator_rejects_missing_request_field():
    payload = request_kwargs()
    payload["evidence"] = evidence_kwargs()
    payload["decision"] = QueueGovernanceDecision.PREPARE_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY
    payload["request_id"] = ""
    with pytest.raises(QueueGovernanceValidationError, match="MISSING_QUEUE_GOVERNANCE_REQUEST_FIELDS"):
        validate_queue_governance_request(payload)
