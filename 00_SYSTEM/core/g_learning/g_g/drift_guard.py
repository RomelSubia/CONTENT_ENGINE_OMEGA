from __future__ import annotations

from typing import Dict, Tuple


def drift_guard(input_data: Dict, approval: Dict, snapshot: Dict, repo_state: Dict) -> Tuple[bool, str]:
    if approval["source_plan_hash"] != input_data["plan_hash"]:
        return False, "PLAN_HASH_DRIFT"

    if approval["source_repo_head"] != repo_state["repo_head"]:
        return False, "REPO_HEAD_DRIFT"

    if approval["source_snapshot_hash"] != snapshot["snapshot_hash"]:
        return False, "SNAPSHOT_HASH_DRIFT"

    return True, "NO_DRIFT"
