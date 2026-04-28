from __future__ import annotations

from typing import Dict, Tuple

from .constants import REQUIRED_PERMISSION_USAGE_KEYS


def validate_permission_usage(permission_usage: Dict) -> Tuple[bool, str]:
    if not isinstance(permission_usage, dict):
        return False, "PERMISSION_USAGE_NOT_DICT"

    missing = [key for key in REQUIRED_PERMISSION_USAGE_KEYS if key not in permission_usage]
    if missing:
        return False, "MISSING_PERMISSION_USAGE_KEYS:" + ",".join(missing)

    if permission_usage["used"] is not False:
        return False, "PERMISSION_ALREADY_USED"

    if permission_usage["single_use"] is not True:
        return False, "PERMISSION_MUST_BE_SINGLE_USE"

    if not isinstance(permission_usage["usage_hash"], str) or not permission_usage["usage_hash"]:
        return False, "INVALID_USAGE_HASH"

    return True, "PERMISSION_USAGE_OK"
