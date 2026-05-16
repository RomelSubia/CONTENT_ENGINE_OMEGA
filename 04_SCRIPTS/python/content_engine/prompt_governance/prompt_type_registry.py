from __future__ import annotations

from typing import Any

CONCEPTUAL_TYPES = {
    "IDEA_PROMPT_TEMPLATE_CONCEPTUAL": "CONCEPTUAL_ONLY",
    "HOOK_STRUCTURE_TEMPLATE_CONCEPTUAL": "STRUCTURAL_TEMPLATE",
    "SCRIPT_STRUCTURE_TEMPLATE_CONCEPTUAL": "STRUCTURAL_TEMPLATE",
    "CTA_STRUCTURE_TEMPLATE_CONCEPTUAL": "STRUCTURAL_TEMPLATE",
    "METADATA_STRUCTURE_TEMPLATE_CONCEPTUAL": "STRUCTURAL_TEMPLATE",
    "REVIEW_TEMPLATE_CONCEPTUAL": "REVIEW_TEMPLATE",
    "QUALITY_CHECK_TEMPLATE_CONCEPTUAL": "QUALITY_CHECK_TEMPLATE",
    "CHANNEL_ADAPTATION_TEMPLATE_CONCEPTUAL": "BOUNDARY_TEMPLATE",
}

BLOCKED_TYPES = {
    "FINAL_SCRIPT_PROMPT",
    "READY_TO_PUBLISH_PROMPT",
    "PRODUCTION_PROMPT_PACK",
    "AUTOMATED_VIDEO_PROMPT",
    "QUEUE_READY_PROMPT",
    "PUBLISH_NOW_PROMPT",
    "READY_METADATA_PROMPT",
    "READY_UPLOAD_PACK",
}

ALLOWED_CLASSIFICATIONS = {
    "CONCEPTUAL_ONLY",
    "STRUCTURAL_TEMPLATE",
    "REVIEW_TEMPLATE",
    "QUALITY_CHECK_TEMPLATE",
    "BOUNDARY_TEMPLATE",
}

BLOCKED_CLASSIFICATIONS = {
    "PRODUCTIVE_PROMPT",
    "EXECUTABLE_PROMPT",
    "PUBLISHING_PROMPT",
    "AUTOMATION_PROMPT",
    "FINAL_OUTPUT_PROMPT",
}


def build_prompt_type_registry() -> dict[str, Any]:
    return {"status": "PASS", "conceptual_types": dict(CONCEPTUAL_TYPES), "blocked_types": sorted(BLOCKED_TYPES)}


def validate_prompt_type(prompt_type: str, classification: str | None = None) -> dict[str, Any]:
    if prompt_type in BLOCKED_TYPES:
        return {"status": "BLOCK", "reason": "PRODUCTIVE_PROMPT_TYPE_BLOCKED", "prompt_type": prompt_type}
    if classification in BLOCKED_CLASSIFICATIONS:
        return {"status": "BLOCK", "reason": "PROMPT_CLASSIFICATION_BLOCKED", "classification": classification}
    if prompt_type not in CONCEPTUAL_TYPES:
        return {"status": "BLOCK", "reason": "UNKNOWN_PROMPT_TYPE", "prompt_type": prompt_type}
    expected = CONCEPTUAL_TYPES[prompt_type]
    if classification is not None and classification != expected:
        return {"status": "BLOCK", "reason": "PROMPT_CLASSIFICATION_MISMATCH", "expected": expected, "actual": classification}
    return {"status": "PASS", "prompt_type": prompt_type, "classification": expected}
