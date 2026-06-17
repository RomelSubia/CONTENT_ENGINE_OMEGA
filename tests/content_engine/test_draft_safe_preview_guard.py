from __future__ import annotations

import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_SCRIPTS" / "python"))

from content_engine.content_draft_safe_preview_governance.contracts import SafePreviewError, SafePreviewRequest
from content_engine.content_draft_safe_preview_governance.guard import validate_safe_preview_request


def make_request(**overrides):
    values = {
        "request_id": "REQ-1",
        "candidate_id": "CAND-1",
        "domain_id": "DOMAIN-1",
        "preview_text": "Internal preview only.",
        "classification": "SAFE_INTERNAL_VARIATION",
        "evidence_refs": ["evidence:1"],
        "traceability_refs": ["trace:1"],
        "human_review_required": True,
        "metadata": {},
    }
    values.update(overrides)
    return SafePreviewRequest.from_values(**values)


def test_valid_request_passes_guard():
    request = make_request()
    assert validate_safe_preview_request(request) == request


def test_human_review_false_fails_closed():
    request = make_request(human_review_required=False)
    with pytest.raises(SafePreviewError):
        validate_safe_preview_request(request)


def test_productive_metadata_fails_closed():
    request = make_request(metadata={"queue_payload": {"x": 1}})
    with pytest.raises(SafePreviewError):
        validate_safe_preview_request(request)
