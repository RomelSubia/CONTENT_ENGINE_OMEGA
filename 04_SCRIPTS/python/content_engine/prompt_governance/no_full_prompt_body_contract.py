from __future__ import annotations

from typing import Any

BLOCKED_SHAPES = {
    "complete_prompt_body",
    "copy_paste_ready_prompt",
    "final_script_prompt",
    "complete_caption_prompt",
    "complete_hook_prompt",
    "complete_cta_prompt",
    "ready_metadata_prompt",
    "production_prompt_pack",
}

ALLOWED_SHAPES = {
    "schema",
    "fields",
    "constraints",
    "validation_rules",
    "abstract_negative_examples",
    "conceptual_structure",
    "quality_rules",
    "safety_rules",
}


def validate_no_full_prompt_body(output_shape: str) -> dict[str, Any]:
    if output_shape in BLOCKED_SHAPES:
        return {"status": "BLOCK", "reason": "FULL_PROMPT_BODY_BLOCKED", "output_shape": output_shape}
    if output_shape not in ALLOWED_SHAPES:
        return {"status": "BLOCK", "reason": "UNKNOWN_PROMPT_BODY_SHAPE", "output_shape": output_shape}
    return {"status": "PASS", "output_shape": output_shape}
