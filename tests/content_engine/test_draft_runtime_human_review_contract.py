from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY_ROOT = ROOT / "04_SCRIPTS" / "python"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))


from content_engine.content_draft_runtime_governance.runtime_human_review_contract import validate_human_review

def test_human_review_true_passes():
    assert validate_human_review(True)["status"] == "PASS"

def test_human_review_false_blocks():
    assert validate_human_review(False)["status"] == "FAILED_BLOCKED"

def test_human_review_required():
    assert validate_human_review(True)["human_review_required"] is True

def test_human_review_not_completed_now():
    assert validate_human_review(True)["human_review_completed"] is False

def test_auth_required_for_next_stage():
    assert validate_human_review(True)["human_authorization_required_for_next_stage"] is True

def test_auth_cannot_execute_productive_now():
    assert validate_human_review(True)["human_authorization_can_execute_productive_action_now"] is False

def test_none_blocks():
    assert validate_human_review(None)["status"] == "FAILED_BLOCKED"

def test_zero_blocks():
    assert validate_human_review(0)["status"] == "FAILED_BLOCKED"
