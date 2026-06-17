from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.content_draft_human_review_governance.state_machine import HumanReviewState, transition_state, state_for_decision


def test_allowed_state_transition():
    assert transition_state(HumanReviewState.REVIEW_NOT_STARTED, HumanReviewState.REVIEW_PENDING) == HumanReviewState.REVIEW_PENDING


def test_forbidden_state_transition_fails_closed():
    assert transition_state(HumanReviewState.REVIEW_NOT_STARTED, HumanReviewState.REVIEW_APPROVED) == HumanReviewState.FAILED_CLOSED


def test_decision_state_mapping():
    assert state_for_decision("APPROVE_FOR_FINALIZATION_PLAN_ONLY") == HumanReviewState.REVIEW_APPROVED
    assert state_for_decision("REQUEST_REVISION") == HumanReviewState.REVISION_REQUIRED
    assert state_for_decision("REJECT") == HumanReviewState.REVIEW_REJECTED
