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

    if input_data["subphase"] != "G-D":
        return False, "INVALID_SOURCE_SUBPHASE"

    if input_data["status"] not in {"VALID", "REVIEW_REQUIRED", "BLOCKED"}:
        return False, "INVALID_SOURCE_STATUS"

    if input_data["deterministic"] is not True:
        return False, "SOURCE_NOT_DETERMINISTIC"

    for key in ("approved_for_review", "quarantined", "blocked"):
        if not isinstance(input_data[key], list):
            return False, f"{key.upper()}_NOT_LIST"

    for key in ("input_hash", "risk_hash", "decision_hash", "output_hash"):
        if not isinstance(input_data[key], str) or not input_data[key]:
            return False, f"INVALID_{key.upper()}"

    return True, "INPUT_CONTRACT_OK"
