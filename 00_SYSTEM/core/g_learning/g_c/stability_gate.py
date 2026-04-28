from __future__ import annotations

from typing import Dict, List, Tuple


def stability_impact_gate(recommendation: Dict) -> Tuple[bool, str]:
    impact = recommendation.get("stability_impact")

    if impact == "HIGH":
        return False, "STABILITY_IMPACT_HIGH_BLOCKED"

    if impact == "MEDIUM":
        return True, "REVIEW_REQUIRED"

    return True, "STABILITY_OK"


def validate_stability(recommendations: List[Dict]) -> Tuple[bool, str]:
    for recommendation in recommendations:
        ok, reason = stability_impact_gate(recommendation)
        if not ok:
            return False, reason
    return True, "STABILITY_OK"
