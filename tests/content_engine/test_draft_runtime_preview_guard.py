from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY_ROOT = ROOT / "04_SCRIPTS" / "python"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))


import pytest
from content_engine.content_draft_runtime_governance.runtime_preview_guard import inspect_preview_text

def test_safe_preview_passes():
    assert inspect_preview_text("conceptual idea only")["status"] == "PASS"

@pytest.mark.parametrize("text", ["final caption", "final script", "final CTA", "platform-ready metadata", "publish now", "texto listo para publicar", "hashtags finales", "asset final", "publication link"])
def test_blocked_preview_patterns(text):
    assert inspect_preview_text(text)["status"] == "FAILED_BLOCKED"

def test_preview_requires_human_review():
    assert inspect_preview_text("concept")["human_review_required"] is True

def test_preview_non_publishable():
    assert inspect_preview_text("concept")["non_publishable"] is True

def test_preview_only():
    assert inspect_preview_text("concept")["preview_only"] is True

def test_matched_patterns_reported():
    assert inspect_preview_text("final caption")["matched_patterns"]
