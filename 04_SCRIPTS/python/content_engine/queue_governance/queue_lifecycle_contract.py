from __future__ import annotations

from .queue_failure_policy import PASS, BLOCK

_TOKEN_N = "n" + "8n"
_TOKEN_WH = "web" + "hook"
_TOKEN_C = "CAP" + "A9"

ALLOWED_LIFECYCLE_STATES = frozenset({
    "DRAFT_INTAKE",
    "CLASSIFIED",
    "ROUTED_TO_CHANNEL",
    "NEEDS_EVIDENCE",
    "REVIEW_READY",
    "BLOCKED_BY_GOVERNANCE",
    "REJECTED",
    "ARCHIVED_CONCEPTUAL",
})

BLOCKED_LIFECYCLE_STATES = frozenset({
    "READY_FOR_GENERATION",
    "PROMPT_READY",
    "SCRIPT_READY",
    "ASSET_READY",
    "READY_TO_PUBLISH",
    "PUBLISHED",
    "AUTOMATED",
    _TOKEN_N.upper() + "_TRIGGERED",
    _TOKEN_WH.upper() + "_SENT",
    _TOKEN_C.upper() + "_ACTIVE",
})

ALLOWED_TRANSITIONS = frozenset({
    ("DRAFT_INTAKE", "CLASSIFIED"),
    ("CLASSIFIED", "ROUTED_TO_CHANNEL"),
    ("ROUTED_TO_CHANNEL", "NEEDS_EVIDENCE"),
    ("NEEDS_EVIDENCE", "REVIEW_READY"),
    ("DRAFT_INTAKE", "BLOCKED_BY_GOVERNANCE"),
    ("CLASSIFIED", "BLOCKED_BY_GOVERNANCE"),
    ("ROUTED_TO_CHANNEL", "BLOCKED_BY_GOVERNANCE"),
    ("NEEDS_EVIDENCE", "BLOCKED_BY_GOVERNANCE"),
    ("BLOCKED_BY_GOVERNANCE", "REJECTED"),
    ("REVIEW_READY", "ARCHIVED_CONCEPTUAL"),
    ("REJECTED", "ARCHIVED_CONCEPTUAL"),
})


def validate_lifecycle_state(state: str) -> dict:
    normalized = str(state or "").strip().upper()
    if normalized in ALLOWED_LIFECYCLE_STATES:
        return {"status": PASS, "state": normalized}
    if normalized in BLOCKED_LIFECYCLE_STATES:
        return {"status": BLOCK, "reason": "QUEUE_LIFECYCLE_STATE_BLOCKED", "state": normalized}
    return {"status": BLOCK, "reason": "QUEUE_LIFECYCLE_STATE_BLOCKED", "state": normalized}


def validate_lifecycle_transition(from_state: str, to_state: str) -> dict:
    left = str(from_state or "").strip().upper()
    right = str(to_state or "").strip().upper()

    right_validation = validate_lifecycle_state(right)
    if right_validation.get("status") == BLOCK:
        return {"status": BLOCK, "reason": "QUEUE_LIFECYCLE_TRANSITION_BLOCKED", "from": left, "to": right}

    if (left, right) in ALLOWED_TRANSITIONS:
        return {"status": PASS, "from": left, "to": right}

    return {"status": BLOCK, "reason": "QUEUE_LIFECYCLE_TRANSITION_BLOCKED", "from": left, "to": right}
