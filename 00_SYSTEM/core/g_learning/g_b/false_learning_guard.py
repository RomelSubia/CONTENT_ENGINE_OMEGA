from __future__ import annotations

from typing import Dict, List, Tuple


def false_learning_guard(
    patterns: List[Dict],
    signals: List[Dict],
    evidence_count: int,
    evidence_quality: float,
    contradictions: List[Dict],
) -> Tuple[bool, List[Dict]]:
    flags = []

    if evidence_count < 5:
        flags.append({"type": "SAMPLE_TOO_SMALL"})

    for pattern in patterns:
        if pattern["count"] < 2:
            flags.append({"type": "SINGLE_OCCURRENCE_PATTERN", "pattern": pattern})

    for signal in signals:
        if signal["level"] == "HIGH" and evidence_quality < 0.80:
            flags.append({"type": "FALSE_HIGH_SIGNAL", "signal": signal})

    if contradictions:
        flags.append({"type": "CONTRADICTION_PRESENT", "details": contradictions})

    return len(flags) == 0, flags
