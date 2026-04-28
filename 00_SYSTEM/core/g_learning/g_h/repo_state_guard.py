from __future__ import annotations

from typing import Dict, Tuple

from .constants import REQUIRED_REPO_STATE_KEYS


def validate_repo_state(repo_state: Dict) -> Tuple[bool, str]:
    if not isinstance(repo_state, dict):
        return False, "REPO_STATE_NOT_DICT"

    missing = [key for key in REQUIRED_REPO_STATE_KEYS if key not in repo_state]
    if missing:
        return False, "MISSING_REPO_STATE_KEYS:" + ",".join(missing)

    if repo_state["repo_clean"] is not True:
        return False, "REPO_NOT_CLEAN"

    if repo_state["cache_clean"] is not True:
        return False, "CACHE_NOT_CLEAN"

    if repo_state["head_equals_upstream"] is not True:
        return False, "HEAD_NOT_UPSTREAM"

    if repo_state["no_pycache_tracked"] is not True:
        return False, "PYCACHE_TRACKED"

    return True, "REPO_STATE_OK"
