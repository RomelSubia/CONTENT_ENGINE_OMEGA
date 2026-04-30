from __future__ import annotations

from typing import Dict, Tuple

from .constants import VALID_RISK_LEVELS


def validate_risk(risk: Dict) -> Tuple[bool, str]:
    if not isinstance(risk, dict):
        return False, "RISK_NOT_DICT"

    level = risk.get("risk_level")

    if level not in VALID_RISK_LEVELS:
        return False, "INVALID_RISK_LEVEL"

    if level == "HIGH":
        return False, "RISK_HIGH_BLOCKED"

    if level == "MEDIUM":
        return False, "RISK_MEDIUM_REVIEW_REQUIRED"

    return True, "RISK_LOW_OK"
