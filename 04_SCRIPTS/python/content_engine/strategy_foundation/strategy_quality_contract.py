from __future__ import annotations

from typing import Any

REQUIRED_CRITERIA = [
    "channel_alignment",
    "audience_alignment",
    "pillar_alignment",
    "tone_alignment",
    "intent_alignment",
    "lifecycle_validity",
    "no_cross_channel_contamination",
    "no_execution_trigger",
    "no_publishing_trigger",
    "no_metrics_trigger",
    "evidence_required",
]

ALLOWED_RESULTS = {"PASS", "BLOCK", "NEEDS_REVIEW"}


def build_quality_contract() -> dict[str, Any]:
    return {"status": "PASS", "criteria": list(REQUIRED_CRITERIA), "allowed_results": sorted(ALLOWED_RESULTS)}


def evaluate_quality(item: dict[str, Any]) -> dict[str, Any]:
    missing = [criterion for criterion in REQUIRED_CRITERIA if item.get(criterion) is not True]
    if missing:
        return {"status": "BLOCK", "missing": missing}
    return {"status": "PASS", "missing": []}


def validate_quality_result(result: str) -> dict[str, Any]:
    return {"status": "PASS" if result in ALLOWED_RESULTS else "BLOCK", "result": result}
