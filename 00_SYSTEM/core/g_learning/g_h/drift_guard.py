from __future__ import annotations

from typing import Dict, Tuple


def drift_guard(input_data: Dict, permission: Dict, snapshot: Dict, repo_state: Dict) -> Tuple[bool, str]:
    if permission["source_gate_hash"] != input_data["gate_hash"]:
        return False, "GATE_HASH_DRIFT"

    if permission["source_snapshot_hash"] != input_data["snapshot_hash"]:
        return False, "SNAPSHOT_HASH_DRIFT"

    if permission["source_repo_head"] != repo_state["repo_head"]:
        return False, "REPO_HEAD_DRIFT"

    if snapshot["snapshot_hash"] != input_data["snapshot_hash"]:
        return False, "SNAPSHOT_DECLARATION_DRIFT"

    return True, "NO_DRIFT"
