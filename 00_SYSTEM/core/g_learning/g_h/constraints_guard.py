from __future__ import annotations

from typing import Dict, Tuple


def validate_constraints(constraints: Dict) -> Tuple[bool, str]:
    if not isinstance(constraints, dict):
        return False, "CONSTRAINTS_NOT_DICT"

    required = ("constraints_hash", "immutable", "enforced")
    missing = [key for key in required if key not in constraints]
    if missing:
        return False, "MISSING_CONSTRAINT_KEYS:" + ",".join(missing)

    if constraints["immutable"] is not True:
        return False, "CONSTRAINTS_NOT_IMMUTABLE"

    if constraints["enforced"] is not True:
        return False, "CONSTRAINTS_NOT_ENFORCED"

    return True, "CONSTRAINTS_OK"
