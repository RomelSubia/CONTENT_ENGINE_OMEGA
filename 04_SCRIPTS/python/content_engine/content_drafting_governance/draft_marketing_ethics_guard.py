from __future__ import annotations

ETHICAL_MARKETING_BLOCK_PATTERNS = (
    "última oportunidad falsa",
    "escasez falsa",
    "miedo a perderlo todo",
    "manipula",
    "engaña",
    "presiona",
    "false scarcity",
    "false urgency",
    "exploit fear",
)


def inspect_marketing_ethics(text: str) -> dict[str, object]:
    lowered = text.lower()
    matches = sorted({pattern for pattern in ETHICAL_MARKETING_BLOCK_PATTERNS if pattern in lowered})
    return {
        "blocked": bool(matches),
        "matched_patterns": matches,
        "ethical_persuasion_allowed": not bool(matches),
        "reason": "MARKETING_ETHICS_BLOCK" if matches else "MARKETING_ETHICS_CLEAR",
    }
