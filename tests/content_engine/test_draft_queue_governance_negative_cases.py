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

from content_engine.content_draft_queue_governance.models import QueueGovernanceDecision, QueueGovernanceEvidence, QueueGovernanceRequest
from content_engine.content_draft_queue_governance.policy import QueueGovernancePolicyError, validate_queue_governance_policy
from content_engine.content_draft_queue_governance.queue_record import build_queue_governance_record
from content_engine.content_draft_queue_governance.validator import QueueGovernanceValidationError


def make_payload():
    payload = request_kwargs()
    payload["evidence"] = evidence_kwargs()
    payload["decision"] = QueueGovernanceDecision.PREPARE_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY
    return payload


@pytest.mark.parametrize("decision", ["QUEUE_WRITE_NOW", "CREATE_QUEUE_ITEM_NOW", "UPDATE_QUEUE_ITEM_NOW"])
def test_forbidden_queue_mutation_decisions_fail_closed(decision):
    with pytest.raises(QueueGovernancePolicyError, match="FORBIDDEN_QUEUE_GOVERNANCE_DECISION"):
        validate_queue_governance_policy(decision)


def test_build_rejects_missing_finalization_evidence():
    payload = make_payload()
    payload["evidence"]["finalization_result_reference"] = ""
    with pytest.raises(QueueGovernanceValidationError, match="MISSING_QUEUE_GOVERNANCE_EVIDENCE"):
        build_queue_governance_record(payload)


def test_build_rejects_invalid_finalization_hash():
    payload = make_payload()
    payload["evidence"]["finalization_result_sha256"] = "not-a-hash"
    with pytest.raises(QueueGovernanceValidationError, match="INVALID_SHA256"):
        build_queue_governance_record(payload)


def test_result_asserts_no_productive_side_effects():
    payload = make_payload()
    result = build_queue_governance_record(payload)
    result.assert_no_productive_side_effects()
