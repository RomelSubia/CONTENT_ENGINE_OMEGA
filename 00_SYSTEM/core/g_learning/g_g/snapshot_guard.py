from __future__ import annotations

from typing import Dict, Tuple

from .constants import REQUIRED_SNAPSHOT_KEYS


def validate_snapshot(snapshot: Dict) -> Tuple[bool, str]:
    if not isinstance(snapshot, dict):
        return False, "SNAPSHOT_NOT_DICT"

    missing = [key for key in REQUIRED_SNAPSHOT_KEYS if key not in snapshot]
    if missing:
        return False, "MISSING_SNAPSHOT_KEYS:" + ",".join(missing)

    if snapshot["snapshot_strategy"] != "FULL_REPO_STATE":
        return False, "INVALID_SNAPSHOT_STRATEGY"

    if snapshot["snapshot_target"] != "git_HEAD":
        return False, "INVALID_SNAPSHOT_TARGET"

    return True, "SNAPSHOT_OK"
