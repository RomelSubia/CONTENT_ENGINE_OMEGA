from __future__ import annotations

from typing import Dict, Tuple


def validate_snapshot_declared(snapshot: Dict) -> Tuple[bool, str]:
    if not isinstance(snapshot, dict):
        return False, "SNAPSHOT_NOT_DICT"

    required = ("snapshot_id", "snapshot_hash", "immutable", "content_addressed")
    missing = [key for key in required if key not in snapshot]
    if missing:
        return False, "MISSING_SNAPSHOT_KEYS:" + ",".join(missing)

    if snapshot["immutable"] is not True:
        return False, "SNAPSHOT_NOT_IMMUTABLE"

    if snapshot["content_addressed"] is not True:
        return False, "SNAPSHOT_NOT_CONTENT_ADDRESSED"

    return True, "SNAPSHOT_DECLARED_OK"
