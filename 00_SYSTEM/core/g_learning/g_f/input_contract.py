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

    if input_data["subphase"] != "G-E":
        return False, "INVALID_SOURCE_SUBPHASE"

    if input_data["status"] != "AUTHORIZED_FOR_CONTROLLED_PLAN":
        return False, "SOURCE_NOT_AUTHORIZED"

    if input_data["decision"] != "AUTHORIZED_FOR_CONTROLLED_PLAN":
        return False, "INVALID_SOURCE_DECISION"

    if input_data["deterministic"] is not True:
        return False, "SOURCE_NOT_DETERMINISTIC"

    if not isinstance(input_data["authorized_items"], list):
        return False, "AUTHORIZED_ITEMS_NOT_LIST"

    if len(input_data["authorized_items"]) == 0:
        return False, "AUTHORIZED_ITEMS_EMPTY"

    for key in ("pending_items", "blocked_items"):
        if not isinstance(input_data[key], list):
            return False, f"{key.upper()}_NOT_LIST"

    for key in ("approval_hash", "scope_hash", "lineage_hash", "intent_hash", "authorization_hash", "output_hash"):
        if not isinstance(input_data[key], str) or not input_data[key]:
            return False, f"INVALID_{key.upper()}"

    return True, "INPUT_CONTRACT_OK"
