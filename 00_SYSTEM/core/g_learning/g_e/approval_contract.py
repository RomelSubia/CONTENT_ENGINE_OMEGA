from __future__ import annotations

from typing import Any, Dict, Tuple

from .constants import (
    ALLOWED_INTENT,
    ALLOWED_SCOPE,
    AMBIGUOUS_APPROVALS,
    APPROVAL_VERSION,
    FORBIDDEN_EXECUTION_TERMS,
    REQUIRED_APPROVAL_KEYS,
)


def validate_approval_contract(approval: Dict[str, Any]) -> Tuple[bool, str]:
    if approval is None:
        return False, "APPROVAL_MISSING"

    if not isinstance(approval, dict):
        return False, "APPROVAL_NOT_DICT"

    missing = [key for key in REQUIRED_APPROVAL_KEYS if key not in approval]
    if missing:
        return False, "MISSING_APPROVAL_KEYS:" + ",".join(missing)

    if approval["approval_version"] != APPROVAL_VERSION:
        return False, "INVALID_APPROVAL_VERSION"

    if approval["human_approval"] is not True:
        return False, "HUMAN_APPROVAL_NOT_TRUE"

    if approval["approved_by"] != "Romel":
        return False, "INVALID_APPROVER"

    if approval["identity_verified"] is not True:
        return False, "IDENTITY_NOT_VERIFIED"

    statement = str(approval["approval_statement"]).strip().lower()

    if statement in AMBIGUOUS_APPROVALS:
        return False, "AMBIGUOUS_APPROVAL"

    if len(statement) < 20:
        return False, "APPROVAL_STATEMENT_TOO_WEAK"

    if any(term in statement for term in FORBIDDEN_EXECUTION_TERMS):
        return False, "EXECUTION_ATTEMPT_DETECTED"

    if approval["approval_intent"] != ALLOWED_INTENT:
        return False, "INVALID_APPROVAL_INTENT"

    if approval["approval_scope"] != ALLOWED_SCOPE:
        return False, "INVALID_APPROVAL_SCOPE"

    if not isinstance(approval["approved_items"], list) or not approval["approved_items"]:
        return False, "APPROVED_ITEMS_INVALID"

    if len(approval["approved_items"]) > 10:
        return False, "APPROVED_ITEMS_LIMIT_EXCEEDED"

    if approval["understands_risk"] is not True:
        return False, "RISK_NOT_ACKNOWLEDGED"

    if approval["rollback_acknowledged"] is not True:
        return False, "ROLLBACK_NOT_ACKNOWLEDGED"

    if approval["multi_step_confirmed"] is not True:
        return False, "MULTI_STEP_NOT_CONFIRMED"

    if approval["revocation_status"] != "ACTIVE":
        return False, "APPROVAL_REVOKED_OR_INACTIVE"

    return True, "APPROVAL_CONTRACT_OK"
