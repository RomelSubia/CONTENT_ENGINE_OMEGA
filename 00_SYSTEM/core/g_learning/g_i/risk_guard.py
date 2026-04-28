from __future__ import annotations

from typing import Dict, Tuple

from .constants import VALID_RISK_LEVELS


def validate_risk(input_data: Dict) -> Tuple[bool, str]:
    risk = input_data.get("risk_analysis", {})
    level = risk.get("risk_level")

    if level not in VALID_RISK_LEVELS:
        return False, "INVALID_RISK_LEVEL"

    if level == "HIGH":
        return False, "RISK_HIGH_BLOCKED"

    if level == "MEDIUM":
        return False, "RISK_MEDIUM_REVIEW_REQUIRED"

    return True, "RISK_LOW_OK"
