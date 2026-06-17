from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.content_draft_human_review_governance.models import HumanReviewRequest
from content_engine.content_draft_human_review_governance.validator import validate_human_review


def make_request(**overrides):
    digest = "b" * 64
    base = dict(
        safe_preview_reference="preview://safe/2",
        safe_preview_sha256=digest,
        safe_preview_manifest_reference="manifest://safe/2",
        review_request_id="review-2",
        reviewer_identity="human.reviewer",
        reviewer_role="content_approver",
        review_decision="APPROVE_FOR_FINALIZATION_PLAN_ONLY",
        review_timestamp="2026-06-16T00:00:00Z",
        review_notes_or_reason="approval reason",
        review_evidence_manifest={"safe_preview_sha256": digest},
    )
    base.update(overrides)
    return HumanReviewRequest(**base)


def test_tampered_hash_fails_closed():
    request = make_request(review_evidence_manifest={"safe_preview_sha256": "c" * 64})
    result = validate_human_review(request)
    assert result.status == "FAILED_CLOSED"
    assert "tampered_safe_preview_hash" in result.evidence_errors


def test_invalid_hash_format_fails_closed():
    request = make_request(safe_preview_sha256="not-a-hash", review_evidence_manifest={})
    result = validate_human_review(request)
    assert result.status == "FAILED_CLOSED"
    assert "invalid_safe_preview_sha256" in result.evidence_errors


def test_stale_preview_fails_closed():
    digest = "b" * 64
    request = make_request(review_evidence_manifest={"safe_preview_sha256": digest, "stale_preview": True})
    result = validate_human_review(request)
    assert result.status == "FAILED_CLOSED"
    assert "stale_safe_preview_reference" in result.evidence_errors
