from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.content_draft_human_review_governance.models import HumanReviewRequest
from content_engine.content_draft_human_review_governance.validator import validate_human_review


def test_review_never_opens_productive_operations():
    digest = "e" * 64
    request = HumanReviewRequest(
        safe_preview_reference="preview://safe/4",
        safe_preview_sha256=digest,
        safe_preview_manifest_reference="manifest://safe/4",
        review_request_id="review-4",
        reviewer_identity="human.reviewer",
        reviewer_role="content_approver",
        review_decision="APPROVE_FOR_FINALIZATION_PLAN_ONLY",
        review_timestamp="2026-06-16T00:00:00Z",
        review_notes_or_reason="approval reason",
        review_evidence_manifest={"safe_preview_sha256": digest},
    )
    result = validate_human_review(request)
    assert result.status == "PASS"
    assert result.finalization_allowed_now is False
    assert result.queue_write_allowed_now is False
    assert result.publishing_allowed_now is False
    assert result.automation_allowed_now is False
    assert result.runtime_execution_allowed_now is False
    assert result.draft_creation_allowed_now is False
    assert result.content_generation_allowed_now is False
