from __future__ import annotations

from typing import Dict, Tuple

from .constants import ALLOWED_ACTIONS, ALLOWED_TARGET_TYPES, DENIED_ACTIONS, DENIED_TARGET_TERMS, FORBIDDEN_EXECUTION_TERMS


def validate_step(step: Dict) -> Tuple[bool, str]:
    required = (
        "step_id",
        "action_type",
        "target_type",
        "target",
        "allowed_scope",
        "risk_level",
        "execution_allowed",
    )

    missing = [key for key in required if key not in step]
    if missing:
        return False, "MISSING_STEP_KEYS:" + ",".join(missing)

    if step["action_type"] not in ALLOWED_ACTIONS:
        return False, "ACTION_NOT_ALLOWED"

    if step["action_type"] in DENIED_ACTIONS:
        return False, "DENIED_ACTION_DETECTED"

    if step["target_type"] not in ALLOWED_TARGET_TYPES:
        return False, "TARGET_TYPE_NOT_ALLOWED"

    if step["allowed_scope"] != "READ_ONLY":
        return False, "SCOPE_NOT_READ_ONLY"

    if step["execution_allowed"] is not False:
        return False, "EXECUTION_ALLOWED_FORBIDDEN"

    if step["risk_level"] == "HIGH":
        return False, "HIGH_RISK_PLAN_BLOCKED"

    text = " ".join(str(step.get(k, "")) for k in ("action_type", "target_type", "target")).lower()

    if any(term in text for term in FORBIDDEN_EXECUTION_TERMS):
        return False, "EXECUTION_TOKEN_DETECTED"

    if any(term in text for term in DENIED_TARGET_TERMS):
        return False, "TARGET_SANDBOX_VIOLATION"

    return True, "STEP_OK"


def validate_steps(steps):
    if not isinstance(steps, list) or not steps:
        return False, "STEPS_EMPTY"

    for step in steps:
        ok, reason = validate_step(step)
        if not ok:
            return False, reason

    return True, "STEPS_OK"
