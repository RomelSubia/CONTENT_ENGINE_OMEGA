from __future__ import annotations

from typing import Any

REQUIRED_FIELDS = [
    "prompt_id",
    "prompt_version",
    "channel_id",
    "prompt_type",
    "classification",
    "status",
    "created_by_layer",
    "previous_version",
    "change_reason",
    "content_hash",
    "evidence_reference",
    "created_at_layer_step",
]

ALLOWED_STATUSES = {
    "CONCEPTUAL_DRAFT",
    "CONCEPTUAL_REVIEWED",
    "CONCEPTUAL_APPROVED_FOR_FUTURE_ENGINE",
    "BLOCKED",
    "DEPRECATED",
}

BLOCKED_STATUSES = {
    "PRODUCTION_READY",
    "READY_TO_GENERATE",
    "READY_TO_PUBLISH",
    "ACTIVE_AUTOMATION",
    "QUEUE_READY",
    "PUBLISHING_READY",
}


def validate_prompt_version(payload: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_FIELDS if payload.get(field) in (None, "")]
    if missing:
        return {"status": "BLOCK", "reason": "PROMPT_VERSION_METADATA_MISSING", "missing": missing}
    if payload.get("status") in BLOCKED_STATUSES:
        return {"status": "BLOCK", "reason": "PROMPT_PRODUCTION_STATUS_BLOCKED"}
    if payload.get("status") not in ALLOWED_STATUSES:
        return {"status": "BLOCK", "reason": "UNKNOWN_PROMPT_VERSION_STATUS"}
    return {"status": "PASS", "prompt_id": payload["prompt_id"], "prompt_version": payload["prompt_version"]}
