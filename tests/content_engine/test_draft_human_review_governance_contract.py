from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.content_draft_human_review_governance import HumanReviewRequest, validate_human_review


def valid_request(decision="APPROVE_FOR_FINALIZATION_PLAN_ONLY"):
    digest = "a" * 64
    return HumanReviewRequest(
        safe_preview_reference="preview://safe/1",
        safe_preview_sha256=digest,
        safe_preview_manifest_reference="manifest://safe/1",
        review_request_id="review-1",
        reviewer_identity="human.reviewer",
        reviewer_role="content_approver",
        review_decision=decision,
        review_timestamp="2026-06-16T00:00:00Z",
        review_notes_or_reason="approved for implementation planning only",
        review_evidence_manifest={"safe_preview_sha256": digest},
    )


def test_valid_approval_is_plan_only_and_never_productive():
    result = validate_human_review(valid_request())
    assert result.status == "PASS"
    assert result.approved_for_finalization_plan_only is True
    assert result.finalization_allowed_now is False
    assert result.queue_write_allowed_now is False
    assert result.publishing_allowed_now is False
    assert result.automation_allowed_now is False
    assert result.runtime_execution_allowed_now is False
    assert result.draft_creation_allowed_now is False
    assert result.content_generation_allowed_now is False


def test_missing_reviewer_identity_fails_closed():
    request = valid_request()
    request = HumanReviewRequest(**{**request.__dict__, "reviewer_identity": ""})
    result = validate_human_review(request)
    assert result.status == "FAILED_CLOSED"
    assert "reviewer_identity" in result.missing_fields
