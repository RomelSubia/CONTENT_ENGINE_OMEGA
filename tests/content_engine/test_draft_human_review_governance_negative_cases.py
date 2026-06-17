from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.content_draft_human_review_governance.models import HumanReviewRequest
from content_engine.content_draft_human_review_governance.validator import validate_human_review


def valid_payload():
    digest = "d" * 64
    return dict(
        safe_preview_reference="preview://safe/3",
        safe_preview_sha256=digest,
        safe_preview_manifest_reference="manifest://safe/3",
        review_request_id="review-3",
        reviewer_identity="human.reviewer",
        reviewer_role="content_approver",
        review_decision="APPROVE_FOR_FINALIZATION_PLAN_ONLY",
        review_timestamp="2026-06-16T00:00:00Z",
        review_notes_or_reason="approval reason",
        review_evidence_manifest={"safe_preview_sha256": digest},
    )


def test_all_required_fields_missing_cases_fail_closed():
    required = [
        "safe_preview_reference",
        "safe_preview_sha256",
        "safe_preview_manifest_reference",
        "review_request_id",
        "reviewer_identity",
        "reviewer_role",
        "review_decision",
        "review_timestamp",
        "review_notes_or_reason",
    ]
    for field in required:
        payload = valid_payload()
        payload[field] = ""
        result = validate_human_review(HumanReviewRequest(**payload))
        assert result.status == "FAILED_CLOSED"
        assert field in result.missing_fields


def test_forbidden_decisions_fail_closed():
    for decision in ["APPROVE_FOR_PUBLICATION", "APPROVE_FOR_QUEUE_WRITE", "APPROVE_FOR_AUTOMATION", "APPROVE_FOR_N8N", "APPROVE_FOR_WEBHOOK", "APPROVE_FOR_CAPA9"]:
        payload = valid_payload()
        payload["review_decision"] = decision
        result = validate_human_review(HumanReviewRequest(**payload))
        assert result.status == "FAILED_CLOSED"
        assert result.fail_closed_reason == "forbidden_review_decision"
