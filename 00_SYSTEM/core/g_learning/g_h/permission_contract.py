from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Tuple

from .constants import PERMISSION_SCOPE, PERMISSION_VERSION, REQUIRED_PERMISSION_KEYS


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_permission_contract(permission: Dict, now_iso: str | None = None) -> Tuple[bool, str]:
    if permission is None:
        return False, "PERMISSION_MISSING"

    if not isinstance(permission, dict):
        return False, "PERMISSION_NOT_DICT"

    missing = [key for key in REQUIRED_PERMISSION_KEYS if key not in permission]
    if missing:
        return False, "MISSING_PERMISSION_KEYS:" + ",".join(missing)

    if permission["permission_version"] != PERMISSION_VERSION:
        return False, "INVALID_PERMISSION_VERSION"

    if permission["requested_by"] != "Romel":
        return False, "INVALID_REQUESTER"

    if permission["identity_verified"] is not True:
        return False, "IDENTITY_NOT_VERIFIED"

    if permission["permission_scope"] != PERMISSION_SCOPE:
        return False, "INVALID_PERMISSION_SCOPE"

    if permission["dual_consent"] is not True:
        return False, "DUAL_CONSENT_REQUIRED"

    if permission["secondary_confirmation"] is not True:
        return False, "SECONDARY_CONFIRMATION_REQUIRED"

    if permission["revocation_status"] != "ACTIVE":
        return False, "PERMISSION_REVOKED_OR_INACTIVE"

    statement = str(permission["permission_statement"]).strip().lower()
    if len(statement) < 35:
        return False, "PERMISSION_STATEMENT_TOO_WEAK"

    now = parse_iso(now_iso) if now_iso else datetime.now(timezone.utc)
    expiration = parse_iso(permission["permission_expiration"])
    if now > expiration:
        return False, "PERMISSION_EXPIRED"

    window = permission["execution_window"]
    if not isinstance(window, dict):
        return False, "EXECUTION_WINDOW_NOT_DICT"

    start = parse_iso(window.get("start", "1900-01-01T00:00:00Z"))
    end = parse_iso(window.get("end", "1900-01-01T00:00:00Z"))

    if not (start <= now <= end):
        return False, "OUTSIDE_EXECUTION_WINDOW"

    environment = permission["environment"]
    if not isinstance(environment, dict):
        return False, "ENVIRONMENT_NOT_DICT"

    if environment.get("expected") != environment.get("current"):
        return False, "ENVIRONMENT_MISMATCH"

    if environment.get("locked") is not True:
        return False, "ENVIRONMENT_NOT_LOCKED"

    return True, "PERMISSION_CONTRACT_OK"
