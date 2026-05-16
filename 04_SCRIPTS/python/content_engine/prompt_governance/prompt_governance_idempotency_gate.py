from __future__ import annotations

from typing import Any

BLOCKED_STATES = {
    "BUILT_PENDING_POST_AUDIT",
    "BUILT_POST_AUDITED",
    "VALIDATED_POST_AUDITED",
    "CLOSED_VALIDATED",
}


def validate_prompt_governance_idempotency(existing_status: str | None) -> dict[str, Any]:
    if existing_status in BLOCKED_STATES:
        return {"status": "BLOCK", "reason": "PROMPT_GOVERNANCE_IDEMPOTENCY_BLOCK", "existing_status": existing_status}
    return {"status": "PASS", "existing_status": existing_status}
