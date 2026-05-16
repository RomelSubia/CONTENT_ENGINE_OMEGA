from __future__ import annotations

from typing import Any

REQUIRED_CRITERIA = [
    "channel_alignment",
    "strategy_alignment",
    "audience_alignment",
    "pillar_alignment",
    "tone_alignment",
    "intent_alignment",
    "output_boundary",
    "no_generation_trigger",
    "no_publishing_trigger",
    "no_automation_trigger",
    "evidence_required",
]

VALID_RESULTS = {"PASS", "BLOCK", "NEEDS_REVIEW"}


def validate_prompt_quality(payload: dict[str, Any]) -> dict[str, Any]:
    missing = [criterion for criterion in REQUIRED_CRITERIA if payload.get(criterion) is not True]
    return {"status": "PASS" if not missing else "BLOCK", "missing": missing}


def validate_quality_result(result: str) -> dict[str, Any]:
    return {"status": "PASS" if result in VALID_RESULTS else "BLOCK", "result": result}
