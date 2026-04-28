from __future__ import annotations

from typing import Dict, List


def deduplicate_recommendations(recommendations: List[Dict]) -> List[Dict]:
    seen = set()
    result = []

    for recommendation in recommendations:
        key = (
            recommendation.get("recommendation_id"),
            recommendation.get("statement"),
        )
        if key not in seen:
            seen.add(key)
            result.append(recommendation)

    return result
