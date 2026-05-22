from __future__ import annotations

from .runtime_contracts import BLOCKED_PREVIEW_PATTERNS, PASS
from .runtime_failure_policy import fail_closed

def inspect_preview_text(text: str) -> dict[str, object]:
    normalized = (text or "").lower()
    matched = [pattern for pattern in BLOCKED_PREVIEW_PATTERNS if pattern in normalized]
    if matched:
        return {
            **fail_closed("FINAL_OUTPUT_RISK"),
            "matched_patterns": matched,
        }
    return {
        "status": PASS,
        "preview_only": True,
        "non_publishable": True,
        "human_review_required": True,
        "matched_patterns": [],
    }
