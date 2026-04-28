from __future__ import annotations

from typing import Dict, Tuple

from .constants import VALID_RISK_LEVELS


def validate_risk_analysis(risk: Dict) -> Tuple[bool, str]:
    if not isinstance(risk, dict):
        return False, "RISK_ANALYSIS_NOT_DICT"

    required = ("risk_score", "confidence_score", "risk_level")
    missing = [key for key in required if key not in risk]
    if missing:
        return False, "MISSING_RISK_KEYS:" + ",".join(missing)

    if risk["risk_level"] not in VALID_RISK_LEVELS:
        return False, "INVALID_RISK_LEVEL"

    if risk["risk_level"] == "HIGH":
        return False, "RISK_HIGH_BLOCKED"

    if risk["risk_level"] == "MEDIUM":
        return False, "RISK_MEDIUM_REVIEW_REQUIRED"

    return True, "RISK_LOW_OK"
