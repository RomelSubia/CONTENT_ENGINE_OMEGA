from __future__ import annotations

from typing import Any, Dict, Tuple

from .constants import (
    CONFIDENCE_MIN_REQUIRED,
    EVIDENCE_REF_MIN,
    REQUIRED_RECOMMENDATION_KEYS,
    VALID_RISK_LEVELS,
    VALID_STABILITY_IMPACTS,
)


def validate_recommendation_schema(recommendation: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(recommendation, dict):
        return False, "RECOMMENDATION_NOT_DICT"

    missing = [key for key in REQUIRED_RECOMMENDATION_KEYS if key not in recommendation]
    if missing:
        return False, "MISSING_RECOMMENDATION_KEYS:" + ",".join(missing)

    if not isinstance(recommendation["recommendation_id"], str) or not recommendation["recommendation_id"]:
        return False, "INVALID_RECOMMENDATION_ID"

    if not isinstance(recommendation["confidence_score"], (int, float)):
        return False, "INVALID_CONFIDENCE_SCORE"

    if float(recommendation["confidence_score"]) < CONFIDENCE_MIN_REQUIRED:
        return False, "CONFIDENCE_TOO_LOW"

    if recommendation["risk_level"] not in VALID_RISK_LEVELS:
        return False, "INVALID_RISK_LEVEL"

    if recommendation["stability_impact"] not in VALID_STABILITY_IMPACTS:
        return False, "INVALID_STABILITY_IMPACT"

    if recommendation["touch_scope"] != "READ_ONLY":
        return False, "TOUCH_SCOPE_NOT_READ_ONLY"

    if not isinstance(recommendation["affects_phase"], list):
        return False, "AFFECTS_PHASE_NOT_LIST"

    if recommendation["rollback_required"] is not True:
        return False, "ROLLBACK_REQUIRED"

    if recommendation["auto_apply_allowed"] is not False:
        return False, "AUTO_APPLY_FORBIDDEN"

    if recommendation["requires_human_approval"] is not True:
        return False, "HUMAN_APPROVAL_REQUIRED"

    if recommendation["reversible"] is not True:
        return False, "REVERSIBILITY_REQUIRED"

    if not isinstance(recommendation["evidence_ref"], list):
        return False, "EVIDENCE_REF_NOT_LIST"

    if len(recommendation["evidence_ref"]) < EVIDENCE_REF_MIN:
        return False, "INSUFFICIENT_EVIDENCE_REF"

    return True, "RECOMMENDATION_SCHEMA_OK"


def validate_recommendations(recommendations):
    for recommendation in recommendations:
        ok, reason = validate_recommendation_schema(recommendation)
        if not ok:
            return False, reason
    return True, "RECOMMENDATIONS_OK"
