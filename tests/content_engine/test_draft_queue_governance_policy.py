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

from content_engine.content_draft_queue_governance.policy import (
    QueueGovernancePolicyError,
    blocked_operation_flags,
    validate_queue_governance_policy,
)
from content_engine.content_draft_queue_governance.models import QueueGovernanceDecision


def test_policy_allows_plan_only_decision():
    decision = validate_queue_governance_policy(
        QueueGovernanceDecision.PREPARE_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY
    )
    assert decision is QueueGovernanceDecision.PREPARE_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY


@pytest.mark.parametrize("decision", ["QUEUE_WRITE_NOW", "CREATE_QUEUE_ITEM_NOW", "UPDATE_QUEUE_ITEM_NOW", "PUBLISH_NOW", "AUTOMATE_NOW"])
def test_policy_rejects_forbidden_decisions(decision):
    with pytest.raises(QueueGovernancePolicyError, match="FORBIDDEN_QUEUE_GOVERNANCE_DECISION"):
        validate_queue_governance_policy(decision)


def test_blocked_operation_flags_all_false():
    flags = blocked_operation_flags()
    assert flags
    assert all(value is False for value in flags.values())
    assert flags["queue_write_performed"] is False
    assert flags["queue_item_created"] is False
    assert flags["queue_item_updated"] is False
