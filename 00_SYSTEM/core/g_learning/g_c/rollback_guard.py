from __future__ import annotations

from typing import Dict, Tuple


def rollback_guard(recommendation: Dict) -> Tuple[bool, str]:
    if recommendation.get("rollback_required") is not True:
        return False, "ROLLBACK_REQUIRED"
    if recommendation.get("rollback_strategy") != "MANUAL_ONLY":
        return False, "INVALID_ROLLBACK_STRATEGY"
    if recommendation.get("reversible") is not True:
        return False, "REVERSIBILITY_REQUIRED"
    return True, "ROLLBACK_OK"
