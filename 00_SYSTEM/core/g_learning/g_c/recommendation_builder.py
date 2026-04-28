from __future__ import annotations

from typing import Dict, List

from .hashing import stable_hash


def _source_id(item: Dict, fallback: str) -> str:
    for key in ("pattern_key", "source_id", "id"):
        if key in item:
            return str(item[key])
    return fallback


def build_recommendations(input_data: Dict) -> List[Dict]:
    patterns = input_data.get("patterns", [])
    signals = input_data.get("signals", [])
    hypotheses = input_data.get("hypotheses", [])
    confidence = float(input_data.get("confidence_score", 0.0))

    count = min(len(patterns), len(signals), len(hypotheses))
    recommendations = []

    for index in range(count):
        pattern = patterns[index]
        signal = signals[index]
        hypothesis = hypotheses[index]

        statement = (
            "Review this validated learning signal as a controlled "
            "optimization candidate without applying changes."
        )

        base = {
            "source_pattern_id": _source_id(pattern, f"pattern-{index}"),
            "source_signal_id": _source_id(signal, f"signal-{index}"),
            "source_hypothesis_id": _source_id(hypothesis, f"hypothesis-{index}"),
            "statement": statement,
        }

        recommendation_id = stable_hash(base)

        recommendation = {
            "recommendation_id": recommendation_id,
            "type": "OPTIMIZATION_CANDIDATE",
            "source_pattern": pattern,
            "source_signal": signal,
            "source_hypothesis": hypothesis,
            "statement": statement,
            "evidence_ref": [
                input_data["input_hash"],
                input_data["records_hash"],
                input_data["output_hash"],
            ],
            "confidence_score": confidence,
            "risk_level": "LOW",
            "stability_impact": "LOW",
            "touch_scope": "READ_ONLY",
            "affects_phase": [],
            "requires_human_approval": True,
            "auto_apply_allowed": False,
            "rollback_required": True,
            "rollback_strategy": "MANUAL_ONLY",
            "reversible": True,
            "state": "CANDIDATE_CREATED",
        }

        recommendations.append(recommendation)

    return recommendations
