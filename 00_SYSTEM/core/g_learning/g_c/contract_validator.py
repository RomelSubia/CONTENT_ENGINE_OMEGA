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

    if input_data["subphase"] != "G-B":
        return False, "INVALID_SOURCE_SUBPHASE"

    if input_data["status"] != "VALID":
        return False, "SOURCE_NOT_VALID"

    if input_data["pattern_state"] != "VALID":
        return False, "PATTERN_STATE_NOT_VALID"

    if input_data["false_learning_flags"]:
        return False, "FALSE_LEARNING_FLAGS_PRESENT"

    if input_data["deterministic"] is not True:
        return False, "SOURCE_NOT_DETERMINISTIC"

    if not isinstance(input_data["confidence_score"], (int, float)):
        return False, "INVALID_CONFIDENCE_TYPE"

    if not isinstance(input_data["patterns"], list):
        return False, "PATTERNS_NOT_LIST"

    if not isinstance(input_data["signals"], list):
        return False, "SIGNALS_NOT_LIST"

    if not isinstance(input_data["hypotheses"], list):
        return False, "HYPOTHESES_NOT_LIST"

    for key in ("input_hash", "records_hash", "config_hash", "output_hash"):
        if not isinstance(input_data[key], str) or not input_data[key]:
            return False, f"INVALID_{key.upper()}"

    return True, "INPUT_CONTRACT_OK"
