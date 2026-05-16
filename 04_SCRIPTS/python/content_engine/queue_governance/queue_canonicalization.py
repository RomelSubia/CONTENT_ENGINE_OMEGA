from __future__ import annotations

import hashlib
import json

from .queue_failure_policy import PASS, BLOCK
from .queue_sensitive_data_guard import validate_payload_safety
from .queue_boundary_guard import detect_soft_execution_trigger, detect_human_approval_bypass

ALLOWED_FIELDS = frozenset({
    "schema_version",
    "queue_item_id",
    "created_at_utc",
    "source_type",
    "channel_id",
    "content_intent",
    "idea_title",
    "idea_summary",
    "pillar_id",
    "audience_profile_id",
    "lifecycle_state",
    "priority_score",
    "priority_band",
    "readiness_score",
    "readiness_status",
    "risk_level",
    "evidence_required",
    "evidence_status",
    "generation_allowed",
    "publishing_allowed",
    "queue_write_allowed",
    "blocked_reason",
    "traceability",
})


def _normalize_string(value: str) -> str:
    return " ".join(str(value).replace("\r\n", "\n").replace("\r", "\n").split())


def canonical_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_payload_hash(payload: dict) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def canonicalize_queue_candidate(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {"status": BLOCK, "reason": "CANONICALIZATION_REJECTED_UNSAFE_PAYLOAD", "queue_write_performed": False}

    unknown = sorted(set(payload) - ALLOWED_FIELDS)
    if unknown:
        return {"status": BLOCK, "reason": "CANONICALIZATION_REJECTED_UNSAFE_PAYLOAD", "unknown_fields": unknown, "queue_write_performed": False}

    safety = validate_payload_safety(payload)
    if safety.get("status") == BLOCK:
        return {**safety, "queue_write_performed": False}

    joined_text = " ".join(str(value) for value in payload.values())
    for check in (detect_soft_execution_trigger(joined_text), detect_human_approval_bypass(joined_text)):
        if check.get("status") == BLOCK:
            return {**check, "queue_write_performed": False}

    canonical = {}
    for key in sorted(payload):
        value = payload[key]
        if isinstance(value, str):
            normalized = _normalize_string(value)
            if key in {"source_type", "channel_id", "lifecycle_state", "priority_band", "readiness_status", "risk_level", "schema_version", "evidence_status"}:
                normalized = normalized.upper()
            canonical[key] = normalized
        elif isinstance(value, dict):
            canonical[key] = {str(k): value[k] for k in sorted(value)}
        else:
            canonical[key] = value

    return {
        "status": PASS,
        "canonical_payload": canonical,
        "stable_hash": stable_payload_hash(canonical),
        "queue_write_performed": False,
    }
