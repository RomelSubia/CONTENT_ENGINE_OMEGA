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

from content_engine.content_draft_queue_write_governance.evidence import validate_evidence
from content_engine.content_draft_queue_write_governance.models import QueueWriteGovernanceEvidence


def test_valid_evidence_has_no_errors():
    assert validate_evidence(valid_evidence()) == ()


def test_invalid_hash_fails_closed():
    evidence = QueueWriteGovernanceEvidence(
        queue_governance_reference="ref",
        queue_governance_sha256="bad",
        queue_governance_status=REQUIRED_UPSTREAM_STATUS,
        queue_governance_manifest_reference="manifest",
        source_draft_reference="source",
        source_draft_sha256=VALID_HASH,
        finalization_reference="final",
        finalization_sha256=VALID_HASH,
    )
    assert "INVALID_QUEUE_GOVERNANCE_SHA256" in validate_evidence(evidence)


def test_wrong_upstream_status_fails_closed():
    evidence = valid_evidence()
    bad = QueueWriteGovernanceEvidence(
        queue_governance_reference=evidence.queue_governance_reference,
        queue_governance_sha256=evidence.queue_governance_sha256,
        queue_governance_status="WRONG",
        queue_governance_manifest_reference=evidence.queue_governance_manifest_reference,
        source_draft_reference=evidence.source_draft_reference,
        source_draft_sha256=evidence.source_draft_sha256,
        finalization_reference=evidence.finalization_reference,
        finalization_sha256=evidence.finalization_sha256,
    )
    assert "UPSTREAM_QUEUE_GOVERNANCE_STATUS_INVALID" in validate_evidence(bad)
