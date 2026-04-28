from __future__ import annotations

from pathlib import PurePosixPath
from typing import Dict, Tuple

from .constants import (
    ALLOWED_EXTENSIONS,
    ALLOWED_OPERATION_TYPES,
    ALLOWED_ROOTS,
    BLOCKED_OPERATION_TYPES,
    DENIED_ROOTS,
)


def normalize_target(path: str) -> str:
    return path.replace("\\", "/").strip()


def validate_operation(operation: Dict) -> Tuple[bool, str]:
    required = ("operation_id", "operation_type", "target_path", "max_bytes", "file_type")
    missing = [key for key in required if key not in operation]
    if missing:
        return False, "MISSING_OPERATION_KEYS:" + ",".join(missing)

    op_type = operation["operation_type"]
    if op_type in BLOCKED_OPERATION_TYPES:
        return False, "OPERATION_TYPE_BLOCKED"

    if op_type not in ALLOWED_OPERATION_TYPES:
        return False, "OPERATION_TYPE_NOT_ALLOWED"

    target = normalize_target(str(operation["target_path"]))
    pure = PurePosixPath(target)

    if pure.is_absolute():
        return False, "ABSOLUTE_PATH_BLOCKED"

    if ".." in pure.parts:
        return False, "PATH_TRAVERSAL_BLOCKED"

    if any(target == denied or target.startswith(denied + "/") for denied in DENIED_ROOTS):
        return False, "DENIED_ROOT_BLOCKED"

    if not any(target.startswith(root + "/") or target == root for root in ALLOWED_ROOTS):
        return False, "OUT_OF_SANDBOX"

    if operation["file_type"] not in ALLOWED_EXTENSIONS:
        return False, "FILE_TYPE_BLOCKED"

    if not isinstance(operation["max_bytes"], int) or operation["max_bytes"] <= 0:
        return False, "INVALID_MAX_BYTES"

    if operation["max_bytes"] > 1048576:
        return False, "MAX_BYTES_EXCEEDED"

    return True, "OPERATION_OK"


def validate_operations(operations) -> Tuple[bool, str]:
    if not isinstance(operations, list):
        return False, "OPERATIONS_NOT_LIST"

    if len(operations) > 5:
        return False, "MAX_OPERATIONS_EXCEEDED"

    for operation in operations:
        ok, reason = validate_operation(operation)
        if not ok:
            return False, reason

    return True, "OPERATIONS_OK"
