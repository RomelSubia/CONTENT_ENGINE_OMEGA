from __future__ import annotations

from typing import Dict, List, Tuple

from .constants import PROTECTED_AREAS, SEALED_PHASES


def boundary_guard(recommendation: Dict) -> Tuple[bool, str]:
    if recommendation.get("touch_scope") != "READ_ONLY":
        return False, "BOUNDARY_VIOLATION_TOUCH_SCOPE"

    affected = set(recommendation.get("affects_phase", []))
    if affected.intersection(SEALED_PHASES):
        return False, "SEALED_PHASE_TOUCH_BLOCKED"

    statement = recommendation.get("statement", "").lower()
    forbidden_terms = ("delete", "move file", "patch", "modify code", "auto fix", "execute")
    if any(term in statement for term in forbidden_terms):
        return False, "BOUNDARY_VIOLATION_FORBIDDEN_ACTION"

    for area in PROTECTED_AREAS:
        if area in statement:
            return False, "PROTECTED_AREA_TOUCH_BLOCKED"

    return True, "BOUNDARY_OK"


def validate_boundaries(recommendations: List[Dict]) -> Tuple[bool, str]:
    for recommendation in recommendations:
        ok, reason = boundary_guard(recommendation)
        if not ok:
            return False, reason
    return True, "BOUNDARIES_OK"
