from __future__ import annotations

from .runtime_contracts import PASS
from .runtime_failure_policy import fail_closed

def validate_human_review(required: bool) -> dict[str, object]:
    if required is not True:
        return fail_closed("HUMAN_REVIEW_MISSING")
    return {
        "status": PASS,
        "human_review_required": True,
        "human_review_completed": False,
        "human_authorization_required_for_next_stage": True,
        "human_authorization_can_execute_productive_action_now": False,
    }
