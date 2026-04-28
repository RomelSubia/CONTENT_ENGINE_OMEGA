from __future__ import annotations

from typing import Any, Dict, Tuple

from .constants import (
    ALLOWED_CAPABILITY_MODES,
    ALLOWED_EXECUTION_MODES,
    REQUEST_VERSION,
    REQUIRED_REQUEST_KEYS,
)


def validate_execution_request(request: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(request, dict):
        return False, "REQUEST_NOT_DICT"

    missing = [key for key in REQUIRED_REQUEST_KEYS if key not in request]
    if missing:
        return False, "MISSING_REQUEST_KEYS:" + ",".join(missing)

    if request["request_version"] != REQUEST_VERSION:
        return False, "INVALID_REQUEST_VERSION"

    if request["requested_by"] != "Romel":
        return False, "INVALID_REQUESTER"

    if request["identity_verified"] is not True:
        return False, "IDENTITY_NOT_VERIFIED"

    if request["execution_mode"] not in ALLOWED_EXECUTION_MODES:
        return False, "INVALID_EXECUTION_MODE"

    if request["execution_mode"] != "DRY_RUN_ONLY":
        return False, "CONTROLLED_RUN_LOCKED"

    if request["controlled_run_unlocked"] is not False:
        return False, "CONTROLLED_RUN_UNLOCK_FORBIDDEN"

    if request["physical_mutation_allowed"] is not False:
        return False, "PHYSICAL_MUTATION_FORBIDDEN"

    if request["runner_capability_mode"] not in ALLOWED_CAPABILITY_MODES:
        return False, "CAPABILITY_MODE_NOT_ALLOWED"

    if request["emergency_stop_status"] != "INACTIVE":
        return False, "EMERGENCY_STOP_ACTIVE"

    if not isinstance(request["allowed_operations"], list):
        return False, "ALLOWED_OPERATIONS_NOT_LIST"

    if not isinstance(request["idempotency_key"], str) or not request["idempotency_key"]:
        return False, "INVALID_IDEMPOTENCY_KEY"

    return True, "REQUEST_OK"
