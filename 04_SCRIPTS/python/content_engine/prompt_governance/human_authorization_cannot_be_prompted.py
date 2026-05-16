from __future__ import annotations

from typing import Any

BLOCKED_AUTHORIZATION_PATTERNS = {
    "act_as_authorized",
    "assume_romel_approved",
    "pretend_approval_exists",
    "continue_without_approval",
    "commit_even_if_not_validated",
    "publish_even_if_blocked",
    "simulate_human_authorization",
    "act_as_if_authorized",
}


def validate_human_authorization_prompt(intent: str) -> dict[str, Any]:
    if intent in BLOCKED_AUTHORIZATION_PATTERNS:
        return {"status": "BLOCK", "reason": "HUMAN_AUTHORIZATION_PROMPT_ATTEMPT", "intent": intent}
    return {"status": "PASS", "intent": intent}
