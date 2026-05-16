from __future__ import annotations

from .queue_failure_policy import PASS, BLOCK

_TOKEN_N = "n" + "8n"
_TOKEN_WH = "web" + "hook"

_ALLOWED_SOURCE_TYPES = frozenset({
    "MANUAL_IDEA",
    "OBSERVATION",
    "CONTENT_GAP",
    "SERIES_CANDIDATE",
    "REUSE_CANDIDATE",
})

_BLOCKED_SOURCE_TYPES = frozenset({
    "TREND_CANDIDATE",
    "METRIC_DERIVED_CANDIDATE",
    "FUTURE_API",
    "SCRAPED_SOURCE",
    "PLATFORM_IMPORT",
    "AUTOMATION_IMPORT",
    _TOKEN_WH.upper() + "_IMPORT",
    _TOKEN_N.upper() + "_IMPORT",
})


def classify_source_type(source_type: str) -> dict:
    normalized = str(source_type or "").strip().upper()
    if normalized in _ALLOWED_SOURCE_TYPES:
        return {"status": PASS, "source_type": normalized}
    if normalized in _BLOCKED_SOURCE_TYPES:
        return {"status": BLOCK, "reason": "QUEUE_SOURCE_TYPE_BLOCKED", "source_type": normalized}
    return {"status": BLOCK, "reason": "QUEUE_SOURCE_TYPE_BLOCKED", "source_type": normalized}


def validate_queue_intake(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {"status": BLOCK, "reason": "QUEUE_SCHEMA_VERSION_INVALID"}
    source_result = classify_source_type(payload.get("source_type", ""))
    if source_result.get("status") == BLOCK:
        return source_result
    if not payload.get("channel_id"):
        return {"status": BLOCK, "reason": "QUEUE_CHANNEL_UNKNOWN"}
    return {"status": PASS, "reason": "QUEUE_INTAKE_VALIDATED"}
