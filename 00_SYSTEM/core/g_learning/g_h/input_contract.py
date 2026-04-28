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

    if input_data["subphase"] != "G-G":
        return False, "INVALID_SOURCE_SUBPHASE"

    if input_data["status"] != "READY_FOR_FINAL_EXECUTION_REVIEW":
        return False, "SOURCE_NOT_READY"

    if input_data["execution_permission"] is not False:
        return False, "SOURCE_EXECUTION_PERMISSION_MUST_BE_FALSE"

    if input_data["deterministic"] is not True:
        return False, "SOURCE_NOT_DETERMINISTIC"

    if not isinstance(input_data["execution_gate"], dict) or not input_data["execution_gate"]:
        return False, "INVALID_EXECUTION_GATE"

    for key in ("gate_hash", "snapshot_hash", "validation_hash", "rollback_hash", "drift_hash", "output_hash"):
        if not isinstance(input_data[key], str) or not input_data[key]:
            return False, f"INVALID_{key.upper()}"

    return True, "INPUT_CONTRACT_OK"


def validate_gate_integrity(input_data: Dict[str, Any]) -> Tuple[bool, str]:
    gate = input_data["execution_gate"]

    if gate.get("status") != "READY_FOR_FINAL_EXECUTION_REVIEW":
        return False, "INVALID_GATE_STATUS"

    if gate.get("execution_permission") is not False:
        return False, "GATE_EXECUTION_PERMISSION_MUST_BE_FALSE"

    if gate.get("handoff_target") != "G-H":
        return False, "INVALID_HANDOFF_TARGET"

    required = (
        "execution_gate_id",
        "validated_plan",
        "validated_snapshot",
        "validated_rollback",
        "validated_validation",
        "drift_baseline",
    )

    missing = [key for key in required if key not in gate]
    if missing:
        return False, "MISSING_GATE_KEYS:" + ",".join(missing)

    return True, "GATE_INTEGRITY_OK"
