from __future__ import annotations

from typing import Any

ALLOWED = {"CONCEPTUAL_ONLY", "STRUCTURAL_TEMPLATE", "REVIEW_TEMPLATE", "QUALITY_CHECK_TEMPLATE", "BOUNDARY_TEMPLATE"}
BLOCKED = {"PRODUCTIVE_PROMPT", "EXECUTABLE_PROMPT", "PUBLISHING_PROMPT", "AUTOMATION_PROMPT", "FINAL_OUTPUT_PROMPT"}


def validate_prompt_execution_boundary(payload: dict[str, Any]) -> dict[str, Any]:
    classification = payload.get("classification")
    if classification in BLOCKED:
        return {"status": "BLOCK", "reason": "PROMPT_EXECUTION_BOUNDARY_VIOLATION"}
    if classification not in ALLOWED:
        return {"status": "BLOCK", "reason": "UNKNOWN_PROMPT_EXECUTION_CLASSIFICATION"}
    if payload.get("can_generate_final_content") is True or payload.get("can_execute") is True or payload.get("can_publish") is True:
        return {"status": "BLOCK", "reason": "PROMPT_EXECUTION_BOUNDARY_VIOLATION"}
    return {"status": "PASS", "classification": classification}
