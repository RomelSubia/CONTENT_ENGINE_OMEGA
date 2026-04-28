from __future__ import annotations

from typing import Any, Dict, Tuple

from .constants import REQUIRED_INPUT_KEYS


def validate_input_contract(input_data: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(input_data, dict):
        return False, "INPUT_NOT_DICT"

    missing = [key for key in REQUIRED_INPUT_KEYS if key not in input_data]
    if missing:
        return False, "MISSING_INPUT_KEYS:" + ",".join(missing)

    if input_data["phase"] != "G":
        return False, "INVALID_PHASE"

    if input_data["subphase"] != "G-F":
        return False, "INVALID_SOURCE_SUBPHASE"

    if input_data["status"] != "PLAN_READY_FOR_REVIEW":
        return False, "SOURCE_NOT_PLAN_READY"

    if input_data["decision"] != "PLAN_READY_FOR_REVIEW":
        return False, "INVALID_SOURCE_DECISION"

    if input_data["deterministic"] is not True:
        return False, "SOURCE_NOT_DETERMINISTIC"

    for key in ("controlled_plan", "validation_plan", "rollback_plan", "review_package"):
        if not isinstance(input_data[key], dict) or not input_data[key]:
            return False, f"INVALID_{key.upper()}"

    for key in ("plan_hash", "steps_hash", "diff_hash", "rollback_hash", "validation_hash", "review_hash", "output_hash"):
        if not isinstance(input_data[key], str) or not input_data[key]:
            return False, f"INVALID_{key.upper()}"

    return True, "INPUT_CONTRACT_OK"
