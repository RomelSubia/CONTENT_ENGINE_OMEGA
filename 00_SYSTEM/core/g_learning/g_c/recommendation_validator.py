from __future__ import annotations

from typing import Dict, List, Tuple

from .constants import FORBIDDEN_OUTPUT_TYPES, VALID_OUTPUT_TYPES


REQUIRED_RECOMMENDATION_KEYS = (
    "recommendation_id",
    "type",
    "source_pattern",
    "source_signal",
    "source_hypothesis",
    "statement",
    "evidence_ref",
    "confidence_score",
    "risk_level",
    "stability_impact",
    "touch_scope",
    "affects_phase",
    "requires_human_approval",
    "auto_apply_allowed",
    "rollback_required",
    "rollback_strategy",
    "reversible",
    "state",
)


def validate_recommendation_contract(recommendation: Dict) -> Tuple[bool, str]:
    missing = [key for key in REQUIRED_RECOMMENDATION_KEYS if key not in recommendation]
    if missing:
        return False, "MISSING_RECOMMENDATION_KEYS:" + ",".join(missing)

    if recommendation["type"] in FORBIDDEN_OUTPUT_TYPES:
        return False, "FORBIDDEN_RECOMMENDATION_TYPE"

    if recommendation["type"] not in VALID_OUTPUT_TYPES:
        return False, "INVALID_RECOMMENDATION_TYPE"

    if recommendation["touch_scope"] != "READ_ONLY":
        return False, "INVALID_TOUCH_SCOPE"

    if recommendation["auto_apply_allowed"] is not False:
        return False, "AUTO_APPLY_FORBIDDEN"

    if recommendation["requires_human_approval"] is not True:
        return False, "HUMAN_APPROVAL_REQUIRED"

    if recommendation["rollback_required"] is not True:
        return False, "ROLLBACK_REQUIRED"

    if recommendation["reversible"] is not True:
        return False, "REVERSIBILITY_REQUIRED"

    return True, "RECOMMENDATION_CONTRACT_OK"


def validate_recommendations(recommendations: List[Dict]) -> Tuple[bool, str]:
    for recommendation in recommendations:
        ok, reason = validate_recommendation_contract(recommendation)
        if not ok:
            return False, reason
    return True, "RECOMMENDATIONS_OK"
