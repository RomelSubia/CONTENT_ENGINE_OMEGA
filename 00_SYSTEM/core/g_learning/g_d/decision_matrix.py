from __future__ import annotations

from typing import Dict, List

from .constants import CONFIDENCE_STRONG


def classify_recommendation(recommendation: Dict) -> str:
    risk = recommendation.get("risk_level")
    confidence = float(recommendation.get("confidence_score", 0.0))

    if risk == "CRITICAL":
        return "BLOCK"
    if risk == "HIGH":
        return "QUARANTINE"
    if risk == "MEDIUM":
        return "REVIEW_REQUIRED"
    if risk == "LOW" and confidence >= CONFIDENCE_STRONG:
        return "ALLOW_REVIEW"

    return "REVIEW_REQUIRED"


def quarantine_contract(recommendation: Dict, reason: str) -> Dict:
    return {
        "recommendation_id": recommendation.get("recommendation_id", ""),
        "quarantine_reason": reason,
        "quarantine_level": "HIGH" if recommendation.get("risk_level") == "HIGH" else "MEDIUM",
        "review_required_by_human": True,
        "promotion_blocked": True,
        "source": recommendation,
    }
