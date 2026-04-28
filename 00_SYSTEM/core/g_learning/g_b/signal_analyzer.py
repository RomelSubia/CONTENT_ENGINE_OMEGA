from __future__ import annotations

from typing import Dict, List


def analyze_signals(patterns: List[Dict], evidence_quality: float, confidence: float) -> List[Dict]:
    signals = []

    for pattern in patterns:
        strength = min(1.0, (pattern["count"] / 5) * float(evidence_quality) * confidence)

        level = "LOW"
        if strength > 0.70 and evidence_quality >= 0.80:
            level = "HIGH"
        elif strength >= 0.40:
            level = "MEDIUM"

        signals.append(
            {
                "pattern_key": pattern["pattern_key"],
                "pattern_type": pattern["pattern_type"],
                "strength": round(strength, 4),
                "level": level,
            }
        )

    return signals
