from __future__ import annotations

from typing import Any, Dict


REQUIRED_KEYS = (
    "execution_id",
    "timestamp",
    "source_phase",
    "logs",
    "metrics",
    "decisions",
    "outcomes",
)


def ingest_evidence(input_data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(input_data, dict):
        raise ValueError("INPUT_NOT_DICT")

    missing = [key for key in REQUIRED_KEYS if key not in input_data]
    if missing:
        raise ValueError(f"MISSING_REQUIRED_KEYS:{','.join(missing)}")

    if input_data.get("source_phase") != "F":
        raise ValueError("INVALID_SOURCE_PHASE")

    return {
        "logs": input_data.get("logs") or [],
        "metrics": input_data.get("metrics") or [],
        "decisions": input_data.get("decisions") or [],
        "outcomes": input_data.get("outcomes") or [],
    }
