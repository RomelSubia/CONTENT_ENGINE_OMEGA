from __future__ import annotations

from typing import Any, Dict, Tuple


def validate_evidence(evidence: Dict[str, Any]) -> Tuple[str, float]:
    if not isinstance(evidence, dict):
        return "BLOCKED", 0.0

    expected = ("logs", "metrics", "decisions", "outcomes")

    for key in expected:
        if key not in evidence:
            return "BLOCKED", 0.0
        if evidence[key] is None:
            return "BLOCKED", 0.0
        if not isinstance(evidence[key], list):
            return "BLOCKED", 0.0

    evidence_count = sum(len(evidence[key]) for key in expected)

    if evidence_count == 0:
        return "NO_LEARNING_ALLOWED", 0.0

    quality = min(1.0, evidence_count / 5)

    if quality < 0.80:
        return "REVIEW_REQUIRED", quality

    return "VALID", quality
