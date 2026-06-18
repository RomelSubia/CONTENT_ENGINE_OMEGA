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

from content_engine.content_draft_queue_governance.evidence import (
    QueueGovernanceEvidenceError,
    validate_queue_governance_evidence,
)
from content_engine.content_draft_queue_governance.models import QueueGovernanceEvidence


def test_evidence_validates_dataclass():
    evidence = QueueGovernanceEvidence(**evidence_kwargs())
    assert validate_queue_governance_evidence(evidence) == evidence


def test_evidence_rejects_missing_field():
    payload = evidence_kwargs()
    payload["finalization_result_reference"] = ""
    with pytest.raises(QueueGovernanceEvidenceError, match="MISSING_QUEUE_GOVERNANCE_EVIDENCE"):
        validate_queue_governance_evidence(payload)


def test_evidence_rejects_invalid_sha256():
    payload = evidence_kwargs()
    payload["finalization_result_sha256"] = "bad"
    with pytest.raises(QueueGovernanceEvidenceError, match="INVALID_SHA256"):
        validate_queue_governance_evidence(payload)
