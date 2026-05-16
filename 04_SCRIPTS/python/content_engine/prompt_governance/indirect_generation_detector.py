from __future__ import annotations

from typing import Any

BLOCKED_OUTPUT_HINTS = {
    "final_title",
    "final_hook",
    "final_narration",
    "final_cta",
    "final_caption",
    "ready_publish_structure",
    "complete_content_piece",
    "platform_ready_metadata",
}

ALLOWED_HINTS = {
    "section_schema",
    "structural_guidelines",
    "review_criteria",
    "non_final_outline",
    "conceptual_constraints",
}


def validate_indirect_generation(expected_parts: list[str]) -> dict[str, Any]:
    blocked = [part for part in expected_parts if part in BLOCKED_OUTPUT_HINTS]
    unknown = [part for part in expected_parts if part not in BLOCKED_OUTPUT_HINTS and part not in ALLOWED_HINTS]
    if blocked:
        return {"status": "BLOCK", "reason": "INDIRECT_GENERATION_DETECTED", "blocked": blocked}
    if unknown:
        return {"status": "BLOCK", "reason": "UNKNOWN_GENERATION_PARTS", "unknown": unknown}
    return {"status": "PASS", "parts": expected_parts}
