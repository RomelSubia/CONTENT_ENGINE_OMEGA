from __future__ import annotations

from typing import Dict, List

from .constants import CONFIDENCE_MIN_GENERATE


def no_action_required(input_data: Dict) -> bool:
    if float(input_data["confidence_score"]) < CONFIDENCE_MIN_GENERATE:
        return True

    if not input_data.get("patterns"):
        return True

    if not input_data.get("signals"):
        return True

    if not input_data.get("hypotheses"):
        return True

    return False


def build_no_recommendation() -> Dict:
    return {
        "status": "NO_RECOMMENDATION",
        "recommendations": [],
        "quarantined": [],
        "review_queue": [],
        "recommendation_count": 0,
        "decision": "NO_RECOMMENDATION",
    }
