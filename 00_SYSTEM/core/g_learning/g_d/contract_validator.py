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

    if input_data["subphase"] != "G-C":
        return False, "INVALID_SOURCE_SUBPHASE"

    if input_data["status"] not in {"VALID", "NO_RECOMMENDATION", "BLOCKED"}:
        return False, "INVALID_SOURCE_STATUS"

    if input_data["deterministic"] is not True:
        return False, "SOURCE_NOT_DETERMINISTIC"

    if not isinstance(input_data["recommendations"], list):
        return False, "RECOMMENDATIONS_NOT_LIST"

    if not isinstance(input_data["quarantined"], list):
        return False, "QUARANTINED_NOT_LIST"

    if not isinstance(input_data["review_queue"], list):
        return False, "REVIEW_QUEUE_NOT_LIST"

    if not isinstance(input_data["recommendation_count"], int):
        return False, "INVALID_RECOMMENDATION_COUNT"

    if input_data["recommendation_count"] != len(input_data["recommendations"]):
        return False, "RECOMMENDATION_COUNT_MISMATCH"

    if input_data["recommendation_count"] == 0 and input_data["decision"] == "READY_FOR_REVIEW":
        return False, "EMPTY_RECOMMENDATIONS_READY_FOR_REVIEW"

    for key in ("input_hash", "recommendation_hash", "config_hash", "output_hash"):
        if not isinstance(input_data[key], str) or not input_data[key]:
            return False, f"INVALID_{key.upper()}"

    return True, "INPUT_CONTRACT_OK"
