from __future__ import annotations

from typing import Any

BLOCKED_OUTPUTS = {
    "final_script",
    "ready_post",
    "ready_caption",
    "ready_metadata",
    "ready_thumbnail_prompt",
    "ready_video_script",
    "ready_publish_pack",
    "ready_upload_pack",
    "ready_queue_item",
    "ready_asset_instruction",
}

ALLOWED_OUTPUTS = {
    "structure_schema",
    "quality_rules",
    "review_criteria",
    "conceptual_template_shape",
    "channel_prompt_constraints",
    "safety_boundary_rules",
    "versioning_rules",
    "evidence_rules",
    "non_final_outline",
}


def validate_no_final_output(expected_output: str) -> dict[str, Any]:
    if expected_output in BLOCKED_OUTPUTS:
        return {"status": "BLOCK", "reason": "NO_FINAL_OUTPUT_VIOLATION", "expected_output": expected_output}
    if expected_output not in ALLOWED_OUTPUTS:
        return {"status": "BLOCK", "reason": "UNKNOWN_OUTPUT_SHAPE", "expected_output": expected_output}
    return {"status": "PASS", "expected_output": expected_output}
