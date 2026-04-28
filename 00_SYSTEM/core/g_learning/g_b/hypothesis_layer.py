from __future__ import annotations

from typing import Dict, List


CAUSAL_TERMS = (
    "caused",
    "causes",
    "cause",
    "provoked",
    "generated directly",
    "directly generated",
    "causó",
    "provocó",
    "generó directamente",
)


def build_hypotheses(patterns: List[Dict]) -> List[Dict]:
    hypotheses = []

    for pattern in patterns:
        hypotheses.append(
            {
                "hypothesis_type": "ASSOCIATION_ONLY",
                "statement": (
                    f"{pattern['pattern_type']} appears associated with "
                    f"{pattern['category']} under current evidence"
                ),
                "causal_claim": False,
                "pattern_key": pattern["pattern_key"],
            }
        )

    return hypotheses


def anti_causality_guard(hypotheses: List[Dict]) -> bool:
    for hypothesis in hypotheses:
        statement = hypothesis.get("statement", "").lower()
        if hypothesis.get("causal_claim") is True:
            return False
        if any(term in statement for term in CAUSAL_TERMS):
            return False
    return True
