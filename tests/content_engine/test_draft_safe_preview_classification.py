from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_SCRIPTS" / "python"))

from content_engine.content_draft_safe_preview_governance.classification import (
    is_allowed_classification,
    is_blocked_classification,
)


def test_allowed_classification():
    assert is_allowed_classification("SAFE_CONCEPTUAL_PREVIEW") is True
    assert is_allowed_classification("SAFE_INTERNAL_VARIATION") is True
    assert is_allowed_classification("SAFE_STRUCTURE_PREVIEW") is True


def test_blocked_classification():
    assert is_blocked_classification("FINAL_DRAFT") is True
    assert is_blocked_classification("QUEUE_READY_PAYLOAD") is True
    assert is_blocked_classification("PUBLICATION_PAYLOAD") is True
