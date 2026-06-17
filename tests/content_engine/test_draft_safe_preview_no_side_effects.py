from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_SCRIPTS" / "python"))

from content_engine.content_draft_safe_preview_governance.audit import (
    assert_no_productive_flags,
    build_audit_bundle,
)
from content_engine.content_draft_safe_preview_governance.contracts import SafePreviewRequest
from content_engine.content_draft_safe_preview_governance.preview import build_safe_preview


def test_safe_preview_has_no_productive_side_effect_flags():
    request = SafePreviewRequest.from_values(
        request_id="REQ-1",
        candidate_id="CAND-1",
        domain_id="DOMAIN-1",
        preview_text="Internal preview only.",
        classification="SAFE_CONCEPTUAL_PREVIEW",
        evidence_refs=["evidence:1"],
        traceability_refs=["trace:1"],
    )

    result = build_safe_preview(request)
    audit = build_audit_bundle(result)

    assert assert_no_productive_flags(result.blocked_productive_flags) is True
    assert audit["productive_operations_blocked"] is True
    assert result.blocked_productive_flags["runtime_execution_started"] is False
    assert result.blocked_productive_flags["draft_creation_started"] is False
    assert result.blocked_productive_flags["content_generation_started"] is False
    assert result.blocked_productive_flags["queue_write_performed"] is False
    assert result.blocked_productive_flags["publishing_started"] is False
    assert result.blocked_productive_flags["automation_started"] is False
