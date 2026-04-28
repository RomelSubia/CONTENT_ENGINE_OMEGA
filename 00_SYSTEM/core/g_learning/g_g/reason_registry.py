from __future__ import annotations

from typing import Dict


def reason(reason_code: str, detail: str = "", origin: str = "G-G") -> Dict:
    return {
        "reason_code": reason_code,
        "reason_detail": detail or reason_code,
        "origin_layer": origin,
        "timestamp": "DETERMINISTIC_NOT_RUNTIME_TIME",
    }
