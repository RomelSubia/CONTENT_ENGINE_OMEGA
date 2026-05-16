from __future__ import annotations

from typing import Any

BLOCKED_OVERRIDE_PATTERNS = {
    "ignore_previous_rules",
    "bypass_governance",
    "skip_evidence",
    "override_channel_boundary",
    "simulate_authorization",
    "pretend_approved",
    "disable_safety",
    "ignore_fail_closed",
    "force_commit",
    "force_push",
    "act_as_if_authorized",
}


def validate_policy_override(intent: str) -> dict[str, Any]:
    if intent in BLOCKED_OVERRIDE_PATTERNS:
        return {"status": "BLOCK", "reason": "PROMPT_POLICY_OVERRIDE_BLOCKED", "intent": intent}
    return {"status": "PASS", "intent": intent}
