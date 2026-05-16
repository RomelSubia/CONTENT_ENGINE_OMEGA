from __future__ import annotations

import re

from .queue_failure_policy import PASS, BLOCK
from .queue_lifecycle_contract import validate_lifecycle_state
from .queue_intake_contract import classify_source_type
from .queue_channel_router import validate_channel_id

SCHEMA_VERSION = "QUEUE_ITEM_SCHEMA_V1"
QUEUE_ITEM_ID_RE = re.compile(r"^QG-\d{8}-\d{6}-[A-F0-9]{8}$")
UTC_Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

MANDATORY_FIELDS = (
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
    "readiness_score",
    "risk_level",
    "evidence_status",
    "generation_allowed",
    "publishing_allowed",
    "queue_write_allowed",
    "traceability",
)


def validate_queue_item_id(queue_item_id: str) -> dict:
    value = str(queue_item_id or "")
    if "/" in value or "\\" in value or ":" in value:
        return {"status": BLOCK, "reason": "QUEUE_ITEM_ID_PATH_LIKE"}
    if "@" in value:
        return {"status": BLOCK, "reason": "QUEUE_ITEM_ID_PERSONAL_IDENTIFIER"}
    if not QUEUE_ITEM_ID_RE.match(value):
        return {"status": BLOCK, "reason": "QUEUE_ITEM_ID_INVALID_FORMAT"}
    return {"status": PASS, "queue_item_id": value}


def validate_created_at_utc(created_at_utc: str) -> dict:
    value = str(created_at_utc or "")
    if not UTC_Z_RE.match(value):
        return {"status": BLOCK, "reason": "QUEUE_CREATED_AT_NOT_UTC"}
    return {"status": PASS, "created_at_utc": value}


def validate_queue_item_schema(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {"status": BLOCK, "reason": "QUEUE_SCHEMA_VERSION_INVALID"}

    missing = [field for field in MANDATORY_FIELDS if field not in payload]
    if missing:
        if "schema_version" in missing:
            return {"status": BLOCK, "reason": "QUEUE_SCHEMA_VERSION_MISSING", "missing": missing}
        return {"status": BLOCK, "reason": "QUEUE_SCHEMA_VERSION_INVALID", "missing": missing}

    if payload.get("schema_version") != SCHEMA_VERSION:
        return {"status": BLOCK, "reason": "QUEUE_SCHEMA_VERSION_INVALID"}

    for check in (
        validate_queue_item_id(payload.get("queue_item_id")),
        validate_created_at_utc(payload.get("created_at_utc")),
        classify_source_type(payload.get("source_type")),
        validate_channel_id(payload.get("channel_id")),
        validate_lifecycle_state(payload.get("lifecycle_state")),
    ):
        if check.get("status") == BLOCK:
            return check

    for flag in ("generation_allowed", "publishing_allowed", "queue_write_allowed"):
        if payload.get(flag) is not False:
            return {"status": BLOCK, "reason": "QUEUE_REVIEW_READY_NOT_GENERATION_READY", "field": flag}

    return {
        "status": PASS,
        "reason": "QUEUE_ITEM_SCHEMA_VALIDATED",
        "queue_write_allowed": False,
        "generation_allowed": False,
        "publishing_allowed": False,
    }


def build_conceptual_queue_item(payload: dict) -> dict:
    validation = validate_queue_item_schema(payload)
    if validation.get("status") == BLOCK:
        return validation
    return {
        "status": PASS,
        "queue_item_draft": dict(payload),
        "real_queue_item": None,
        "queue_write_performed": False,
    }
