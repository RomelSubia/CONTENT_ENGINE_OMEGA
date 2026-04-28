from __future__ import annotations

from typing import Dict, Tuple

from .constants import HIDDEN_OPTIMIZATION_TERMS


def hidden_optimization_guard(recommendation: Dict) -> Tuple[bool, str]:
    statement = str(recommendation.get("statement", "")).lower()
    if any(term in statement for term in HIDDEN_OPTIMIZATION_TERMS):
        return False, "FALSE_OPTIMIZATION_DETECTED"
    return True, "NO_FALSE_OPTIMIZATION"
