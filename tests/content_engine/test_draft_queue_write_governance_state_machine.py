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

from content_engine.content_draft_queue_write_governance.models import READY_STATUS
from content_engine.content_draft_queue_write_governance.state_machine import (
    EVIDENCE_VALIDATED,
    INTENT_PREPARED,
    POLICY_VALIDATED,
    RECEIVED,
    fail_closed_state,
    validate_transition,
)


def test_allowed_state_transition_chain():
    assert validate_transition(RECEIVED, EVIDENCE_VALIDATED) == (True, None)
    assert validate_transition(EVIDENCE_VALIDATED, POLICY_VALIDATED) == (True, None)
    assert validate_transition(POLICY_VALIDATED, INTENT_PREPARED) == (True, None)
    assert validate_transition(INTENT_PREPARED, READY_STATUS) == (True, None)


def test_forbidden_productive_state_fails():
    ok, error = validate_transition(INTENT_PREPARED, "QUEUE_WRITTEN")
    assert ok is False
    assert error == "FORBIDDEN_PRODUCTIVE_STATE"


def test_invalid_transition_fails_closed():
    ok, error = validate_transition(RECEIVED, READY_STATUS)
    assert ok is False
    assert error == "INVALID_QUEUE_WRITE_GOVERNANCE_TRANSITION"
    assert fail_closed_state() == "FAILED_CLOSED"
