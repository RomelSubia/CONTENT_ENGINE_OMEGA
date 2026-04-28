from __future__ import annotations

from typing import Dict, List


def calculate_confidence(patterns: List[Dict], evidence_quality: float, contradictions: List[Dict]) -> float:
    if not patterns:
        return 0.0

    total_frequency = sum(pattern["count"] for pattern in patterns)
    frequency_score = min(1.0, total_frequency / 10)

    consistency_score = 1.0
    if contradictions:
        consistency_score = 0.30

    confidence = frequency_score * float(evidence_quality) * consistency_score

    # Ceiling: confidence can never exceed evidence quality or 0.95
    confidence = min(confidence, float(evidence_quality), 0.95)

    return round(confidence, 4)
