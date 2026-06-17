from __future__ import annotations

import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_SCRIPTS" / "python"))

from content_engine.content_draft_safe_preview_governance.contracts import SafePreviewError, SafePreviewRequest
from content_engine.content_draft_safe_preview_governance.preview import build_safe_preview


def make_request(**overrides):
    values = {
        "request_id": "REQ-1",
        "candidate_id": "CAND-1",
        "domain_id": "DOMAIN-1",
        "preview_text": "Internal preview only.",
        "classification": "SAFE_STRUCTURE_PREVIEW",
        "evidence_refs": ["evidence:1"],
        "traceability_refs": ["trace:1"],
        "human_review_required": True,
        "metadata": {},
    }
    values.update(overrides)
    return SafePreviewRequest.from_values(**values)


@pytest.mark.parametrize(
    "field,value",
    [
        ("request_id", ""),
        ("candidate_id", ""),
        ("domain_id", ""),
        ("preview_text", ""),
        ("evidence_refs", []),
        ("traceability_refs", []),
    ],
)
def test_missing_required_fields_fail_closed(field, value):
    request = make_request(**{field: value})
    with pytest.raises(SafePreviewError):
        build_safe_preview(request)


@pytest.mark.parametrize(
    "classification",
    [
        "FINAL_DRAFT",
        "PLATFORM_READY_COPY",
        "QUEUE_READY_PAYLOAD",
        "PUBLICATION_PAYLOAD",
        "AUTOMATION_PAYLOAD",
        "UNKNOWN",
    ],
)
def test_blocked_or_unknown_classifications_fail_closed(classification):
    request = make_request(classification=classification)
    with pytest.raises(SafePreviewError):
        build_safe_preview(request)
