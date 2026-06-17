from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_SCRIPTS" / "python"))

from content_engine.content_draft_safe_preview_governance.contracts import SafePreviewRequest
from content_engine.content_draft_safe_preview_governance.preview import build_safe_preview


def test_safe_preview_request_builds_non_final_result():
    request = SafePreviewRequest.from_values(
        request_id="REQ-1",
        candidate_id="CAND-1",
        domain_id="DOMAIN-1",
        preview_text="Internal structure preview only.",
        classification="SAFE_CONCEPTUAL_PREVIEW",
        evidence_refs=["evidence:1"],
        traceability_refs=["trace:1"],
    )

    result = build_safe_preview(request)

    assert result.preview_label == "INTERNAL_SAFE_PREVIEW_NON_FINAL"
    assert result.human_review_required is True
    assert result.blocked_productive_flags["queue_write_performed"] is False
    assert result.blocked_productive_flags["publishing_started"] is False
