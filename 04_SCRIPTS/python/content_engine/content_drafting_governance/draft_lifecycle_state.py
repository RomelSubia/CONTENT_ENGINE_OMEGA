from __future__ import annotations

ALLOWED_LIFECYCLE_STATES = {
    "CONCEPTUAL_ONLY",
    "DRAFT_GOVERNANCE_REVIEW_REQUIRED",
    "BLOCKED_BY_POLICY",
    "BLOCKED_BY_MATURITY",
    "BLOCKED_BY_RISK",
    "READY_FOR_HUMAN_REVIEW_ONLY",
}

DISALLOWED_LIFECYCLE_STATES = {
    "PUBLISHED",
    "FINAL",
    "SCHEDULED",
    "AUTO_APPROVED",
}


def validate_lifecycle_state(value: str) -> str:
    if value in DISALLOWED_LIFECYCLE_STATES:
        raise ValueError(f"lifecycle state is not permitted: {value}")
    if value not in ALLOWED_LIFECYCLE_STATES:
        raise ValueError(f"unknown lifecycle state: {value}")
    return value
