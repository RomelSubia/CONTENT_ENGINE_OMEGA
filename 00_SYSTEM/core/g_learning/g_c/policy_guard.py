from __future__ import annotations

from typing import Dict, List, Tuple

from .rollback_guard import rollback_guard


def policy_conflict_detector(recommendation: Dict) -> Tuple[bool, str]:
    statement = recommendation.get("statement", "").lower()
    conflicts = (
        "disable fail-closed",
        "reduce validation",
        "bypass approval",
        "auto apply",
        "modify sealed phase",
    )

    if any(conflict in statement for conflict in conflicts):
        return False, "POLICY_CONFLICT_DETECTED"

    ok, reason = rollback_guard(recommendation)
    if not ok:
        return False, reason

    return True, "POLICY_OK"


def validate_policy(recommendations: List[Dict]) -> Tuple[bool, str]:
    for recommendation in recommendations:
        ok, reason = policy_conflict_detector(recommendation)
        if not ok:
            return False, reason
    return True, "POLICY_OK"
