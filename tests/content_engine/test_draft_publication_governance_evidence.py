from content_engine.content_draft_publication_governance.evidence import validate_evidence
from content_engine.content_draft_publication_governance.models import (
    REQUIRED_PUBLICATION_READINESS_MAP_STATUS,
    REQUIRED_QUEUE_WRITE_GOVERNANCE_STATUS,
    PublicationGovernanceEvidence,
)


VALID_HASH = "a" * 64


def valid_evidence(**overrides):
    data = {
        "queue_write_governance_gate_close_reference": "manifests/qwg-gate.json",
        "queue_write_governance_gate_close_sha256": VALID_HASH,
        "queue_write_governance_status": REQUIRED_QUEUE_WRITE_GOVERNANCE_STATUS,
        "publication_readiness_map_reference": "manifests/publication-map.json",
        "publication_readiness_map_sha256": VALID_HASH,
        "publication_readiness_map_status": REQUIRED_PUBLICATION_READINESS_MAP_STATUS,
        "safe_preview_reference": "reports/safe-preview.json",
        "safe_preview_sha256": VALID_HASH,
        "human_review_reference": "reports/human-review.json",
        "human_review_sha256": VALID_HASH,
        "finalization_reference": "reports/finalization.json",
        "finalization_sha256": VALID_HASH,
    }
    data.update(overrides)
    return PublicationGovernanceEvidence(**data)


def test_valid_evidence_passes():
    ok, errors = validate_evidence(valid_evidence())
    assert ok is True
    assert errors == ()


def test_hash_mismatch_fails_closed():
    ok, errors = validate_evidence(valid_evidence(safe_preview_sha256="bad"))
    assert ok is False
    assert "INVALID_SAFE_PREVIEW_SHA256" in errors


def test_wrong_upstream_status_fails_closed():
    ok, errors = validate_evidence(valid_evidence(queue_write_governance_status="OLD"))
    assert ok is False
    assert "STALE_OR_INVALID_QUEUE_WRITE_GOVERNANCE" in errors


def test_missing_human_review_fails_closed():
    ok, errors = validate_evidence(valid_evidence(human_review_status="MISSING"))
    assert ok is False
    assert "MISSING_HUMAN_REVIEW" in errors
