from __future__ import annotations

from typing import Any, Dict, Tuple

from .constants import REQUIRED_INPUT_KEYS, REQUIRED_RECORD_KEYS, VALID_RECORD_TYPES


def validate_input_contract(input_data: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(input_data, dict):
        return False, "INPUT_NOT_DICT"

    missing = [key for key in REQUIRED_INPUT_KEYS if key not in input_data]
    if missing:
        return False, "MISSING_INPUT_KEYS:" + ",".join(missing)

    if input_data["phase"] != "G":
        return False, "INVALID_PHASE"

    if input_data["source_subphase"] != "G-A":
        return False, "INVALID_SOURCE_SUBPHASE"

    if input_data["status"] != "VALID":
        return False, "SOURCE_NOT_VALID"

    if not isinstance(input_data["evidence_quality"], (int, float)):
        return False, "INVALID_EVIDENCE_QUALITY_TYPE"

    if float(input_data["evidence_quality"]) < 0.80:
        return False, "EVIDENCE_QUALITY_TOO_LOW"

    if not isinstance(input_data["evidence_count"], int):
        return False, "INVALID_EVIDENCE_COUNT_TYPE"

    if input_data["evidence_count"] < 5:
        return False, "EVIDENCE_COUNT_TOO_LOW"

    if not isinstance(input_data["records"], list):
        return False, "RECORDS_NOT_LIST"

    if len(input_data["records"]) == 0:
        return False, "RECORDS_EMPTY"

    if not input_data["input_hash"]:
        return False, "MISSING_INPUT_HASH"

    if not input_data["output_hash"]:
        return False, "MISSING_OUTPUT_HASH"

    return True, "INPUT_CONTRACT_OK"


def validate_record_schema(record: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(record, dict):
        return False, "RECORD_NOT_DICT"

    missing = [key for key in REQUIRED_RECORD_KEYS if key not in record]
    if missing:
        return False, "MISSING_RECORD_KEYS:" + ",".join(missing)

    if record["type"] not in VALID_RECORD_TYPES:
        return False, "INVALID_RECORD_TYPE"

    if not isinstance(record["index"], int):
        return False, "INVALID_RECORD_INDEX"

    if not isinstance(record["data"], dict):
        return False, "INVALID_RECORD_DATA"

    if not isinstance(record["source_hash"], str) or not record["source_hash"]:
        return False, "INVALID_SOURCE_HASH"

    if record["origin"] != "F":
        return False, "INVALID_RECORD_ORIGIN"

    if not isinstance(record["timestamp"], str) or not record["timestamp"]:
        return False, "INVALID_RECORD_TIMESTAMP"

    return True, "RECORD_SCHEMA_OK"


def validate_records(records):
    for record in records:
        ok, reason = validate_record_schema(record)
        if not ok:
            return False, reason
    return True, "RECORDS_OK"
