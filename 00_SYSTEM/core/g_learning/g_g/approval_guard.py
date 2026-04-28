from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Tuple

from .constants import APPROVAL_SCOPE, APPROVAL_VERSION, REQUIRED_APPROVAL_KEYS


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_final_approval(approval: Dict, now_iso: str | None = None) -> Tuple[bool, str]:
    if approval is None:
        return False, "FINAL_APPROVAL_MISSING"

    if not isinstance(approval, dict):
        return False, "FINAL_APPROVAL_NOT_DICT"

    missing = [key for key in REQUIRED_APPROVAL_KEYS if key not in approval]
    if missing:
        return False, "MISSING_FINAL_APPROVAL_KEYS:" + ",".join(missing)

    if approval["approval_version"] != APPROVAL_VERSION:
        return False, "INVALID_APPROVAL_VERSION"

    if approval["final_approval"] is not True:
        return False, "FINAL_APPROVAL_NOT_TRUE"

    if approval["approved_by"] != "Romel":
        return False, "INVALID_APPROVER"

    if approval["identity_verified"] is not True:
        return False, "IDENTITY_NOT_VERIFIED"

    if approval["approval_scope"] != APPROVAL_SCOPE:
        return False, "INVALID_APPROVAL_SCOPE"

    if approval["understands_execution_risk"] is not True:
        return False, "EXECUTION_RISK_NOT_ACKNOWLEDGED"

    if approval["rollback_acknowledged"] is not True:
        return False, "ROLLBACK_NOT_ACKNOWLEDGED"

    if approval["snapshot_acknowledged"] is not True:
        return False, "SNAPSHOT_NOT_ACKNOWLEDGED"

    if approval["multi_step_confirmed"] is not True:
        return False, "MULTI_STEP_NOT_CONFIRMED"

    if approval["revocation_status"] != "ACTIVE":
        return False, "FINAL_APPROVAL_REVOKED_OR_INACTIVE"

    statement = str(approval["approval_statement"]).strip().lower()
    if len(statement) < 30:
        return False, "FINAL_APPROVAL_STATEMENT_TOO_WEAK"

    now = parse_iso(now_iso) if now_iso else datetime.now(timezone.utc)
    expiration = parse_iso(approval["approval_expiration"])

    if now > expiration:
        return False, "FINAL_APPROVAL_EXPIRED"

    return True, "FINAL_APPROVAL_OK"
