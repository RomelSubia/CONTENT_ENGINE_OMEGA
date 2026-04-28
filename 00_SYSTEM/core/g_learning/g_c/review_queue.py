from __future__ import annotations

from typing import Dict, List, Tuple

from .constants import CONFIDENCE_MIN_PROMOTE, RISK_ORDER


def classify_review(recommendation: Dict) -> str:
    risk = recommendation.get("risk_level", "HIGH")
    confidence = float(recommendation.get("confidence_score", 0.0))

    if RISK_ORDER.get(risk, 4) >= RISK_ORDER["HIGH"]:
        return "BLOCKED"

    if confidence >= CONFIDENCE_MIN_PROMOTE and risk == "LOW":
        return "READY_FOR_REVIEW"

    if risk == "MEDIUM":
        return "QUARANTINED"

    return "REVIEW_REQUIRED"


def build_review_queue(recommendations: List[Dict]) -> Tuple[List[Dict], List[Dict], str]:
    review_queue = []
    quarantined = []
    decision = "NO_RECOMMENDATION"

    for recommendation in recommendations:
        review_state = classify_review(recommendation)
        recommendation["state"] = review_state

        if review_state == "READY_FOR_REVIEW":
            review_queue.append(recommendation)
            decision = "READY_FOR_REVIEW"
        elif review_state == "QUARANTINED":
            quarantined.append(recommendation)
            if decision != "READY_FOR_REVIEW":
                decision = "REVIEW_REQUIRED"
        elif review_state == "REVIEW_REQUIRED":
            review_queue.append(recommendation)
            if decision != "READY_FOR_REVIEW":
                decision = "REVIEW_REQUIRED"
        elif review_state == "BLOCKED":
            quarantined.append(recommendation)
            if decision == "NO_RECOMMENDATION":
                decision = "REVIEW_REQUIRED"

    return review_queue, quarantined, decision
