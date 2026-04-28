from __future__ import annotations

from typing import Dict, List


def reason_entry(reason_code: str, recommendation_id: str = "", detail: str = "") -> Dict:
    return {
        "reason_code": reason_code,
        "recommendation_id": recommendation_id,
        "reason_detail": detail or reason_code,
    }


def add_reason(registry: List[Dict], reason_code: str, recommendation_id: str = "", detail: str = ""):
    registry.append(reason_entry(reason_code, recommendation_id, detail))
