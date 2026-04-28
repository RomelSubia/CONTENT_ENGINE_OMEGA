from __future__ import annotations

from typing import Any, Dict, Tuple

from .constants import REQUIRED_INPUT_KEYS, RUNNER_TARGET


def validate_input_contract(input_data: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(input_data, dict):
        return False, "INPUT_NOT_DICT"

    missing = [key for key in REQUIRED_INPUT_KEYS if key not in input_data]
    if missing:
        return False, "MISSING_INPUT_KEYS:" + ",".join(missing)

    if input_data["phase"] != "G":
        return False, "INVALID_PHASE"

    if input_data["subphase"] != "G-H":
        return False, "INVALID_SOURCE_SUBPHASE"

    if input_data["status"] != "EXECUTION_PERMISSION_READY":
        return False, "SOURCE_NOT_PERMISSION_READY"

    if input_data["logical_execution_permission_ready"] is not True:
        return False, "LOGICAL_PERMISSION_NOT_READY"

    if input_data["execution_permission"] is not False:
        return False, "PHYSICAL_EXECUTION_PERMISSION_MUST_BE_FALSE"

    if input_data["execution_runner_target"] != RUNNER_TARGET:
        return False, "INVALID_RUNNER_TARGET"

    if input_data["deterministic"] is not True:
        return False, "SOURCE_NOT_DETERMINISTIC"

    for key in ("permission_package", "constraints", "trace_chain", "risk_analysis"):
        if not isinstance(input_data[key], dict) or not input_data[key]:
            return False, f"INVALID_{key.upper()}"

    for key in ("permission_hash", "output_hash"):
        if not isinstance(input_data[key], str) or not input_data[key]:
            return False, f"INVALID_{key.upper()}"

    if input_data["permission_package"].get("execution_permission") is not False:
        return False, "PERMISSION_PACKAGE_EXECUTION_MUST_BE_FALSE"

    return True, "INPUT_CONTRACT_OK"
