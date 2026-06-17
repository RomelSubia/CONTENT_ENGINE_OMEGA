from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.content_draft_human_review_governance.policy import ALLOWED_DECISIONS, FORBIDDEN_DECISIONS, decision_fail_reason


def test_allowed_decisions_are_limited():
    assert "APPROVE_FOR_FINALIZATION_PLAN_ONLY" in ALLOWED_DECISIONS
    assert "APPROVE_FOR_PUBLICATION" not in ALLOWED_DECISIONS
    assert "APPROVE_FOR_QUEUE_WRITE" not in ALLOWED_DECISIONS
    assert "APPROVE_FOR_AUTOMATION" not in ALLOWED_DECISIONS


def test_forbidden_productive_decisions_are_blocked():
    assert "APPROVE_FOR_PUBLICATION" in FORBIDDEN_DECISIONS
    assert decision_fail_reason("APPROVE_FOR_PUBLICATION") == "forbidden_review_decision"
    assert decision_fail_reason("APPROVE_FOR_QUEUE_WRITE") == "forbidden_review_decision"
    assert decision_fail_reason("APPROVE_FOR_AUTOMATION") == "forbidden_review_decision"


def test_unknown_decision_fails_closed():
    assert decision_fail_reason("APPROVE_FOR_SOMETHING_ELSE") == "decision_not_allowlisted"
