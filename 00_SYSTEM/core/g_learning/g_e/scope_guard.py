from __future__ import annotations

from typing import Dict, Tuple


def scope_guard(input_data: Dict, approval: Dict) -> Tuple[bool, str]:
    approved_available = {
        item.get("recommendation_id")
        for item in input_data.get("approved_for_review", [])
        if isinstance(item, dict)
    }

    requested = set(approval.get("approved_items", []))

    if not requested:
        return False, "NO_APPROVED_ITEMS"

    if not requested.issubset(approved_available):
        return False, "SCOPE_MISMATCH"

    return True, "SCOPE_OK"
