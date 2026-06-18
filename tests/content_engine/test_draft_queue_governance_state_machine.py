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

from content_engine.content_draft_queue_governance.state_machine import (
    QueueGovernanceState,
    QueueGovernanceStateMachineError,
    transition_queue_governance_state,
)


def test_state_machine_allows_expected_path():
    state = QueueGovernanceState.RECEIVED
    state = transition_queue_governance_state(state, QueueGovernanceState.FINALIZATION_EVIDENCE_VALIDATED)
    state = transition_queue_governance_state(state, QueueGovernanceState.QUEUE_POLICY_VALIDATED)
    state = transition_queue_governance_state(state, QueueGovernanceState.QUEUE_RECORD_PREPARED)
    state = transition_queue_governance_state(state, QueueGovernanceState.READY_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY)

    assert state is QueueGovernanceState.READY_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY


def test_state_machine_rejects_invalid_transition():
    with pytest.raises(QueueGovernanceStateMachineError, match="INVALID_QUEUE_GOVERNANCE_TRANSITION"):
        transition_queue_governance_state(
            QueueGovernanceState.RECEIVED,
            QueueGovernanceState.READY_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY,
        )
