from __future__ import annotations

from .draft_near_final_guard import inspect_near_final_text

PUBLISHABILITY_BLOCK_THRESHOLD = 70


def calculate_publishability_score(text: str) -> int:
    lowered = text.lower()
    score = 0
    markers = [
        "caption",
        "guion",
        "script",
        "cta",
        "publica",
        "post",
        "compra ahora",
        "reserva ahora",
        "link en bio",
        "listo",
    ]
    for marker in markers:
        if marker in lowered:
            score += 10
    if inspect_near_final_text(text)["blocked"] is True:
        score += 50
    return min(score, 100)


def inspect_publishability(text: str) -> dict[str, object]:
    score = calculate_publishability_score(text)
    blocked = score >= PUBLISHABILITY_BLOCK_THRESHOLD
    return {
        "publishability_score": score,
        "blocked": blocked,
        "final_output_allowed": False,
        "reason": "PUBLISHABILITY_BLOCK" if blocked else "PUBLISHABILITY_CLEAR",
    }
