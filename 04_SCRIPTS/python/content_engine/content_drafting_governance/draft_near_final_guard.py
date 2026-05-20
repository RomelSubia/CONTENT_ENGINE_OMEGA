from __future__ import annotations

NEAR_FINAL_PATTERNS = (
    "caption final",
    "guion final",
    "final script",
    "ready-to-post",
    "ready to post",
    "final cta",
    "call to action final",
    "texto final",
    "copy final",
)


def inspect_near_final_text(text: str) -> dict[str, object]:
    lowered = text.lower()
    matches = sorted({pattern for pattern in NEAR_FINAL_PATTERNS if pattern in lowered})
    return {
        "blocked": bool(matches),
        "matched_patterns": matches,
        "reason": "NEAR_FINAL_BLOCK" if matches else "NEAR_FINAL_CLEAR",
    }
