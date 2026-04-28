from __future__ import annotations

from typing import Dict, Tuple


def lineage_guard(input_data: Dict, approval: Dict) -> Tuple[bool, str]:
    if approval["source_input_hash"] != input_data["input_hash"]:
        return False, "INPUT_HASH_MISMATCH"

    if approval["source_risk_hash"] != input_data["risk_hash"]:
        return False, "RISK_HASH_MISMATCH"

    if approval["source_decision_hash"] != input_data["decision_hash"]:
        return False, "DECISION_HASH_MISMATCH"

    return True, "LINEAGE_OK"
