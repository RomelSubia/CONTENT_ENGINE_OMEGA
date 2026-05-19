"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


import re

REQUIRED_FIELDS = (
    "schema_version",
    "queue_item_id",
    "created_at_utc",
    "channel_id",
    "content_intent",
    "idea_title",
    "idea_summary",
    "pillar_id",
    "audience_profile_id",
    "risk_level",
    "evidence_status",
    "traceability",
)

VALID_CHANNELS = {
    "CHANNEL_A_MONEY_MINDSET_CONVERSION",
    "CHANNEL_D_AI_TECH_PERSONAL_BRAND",
    "CHANNEL_B_CURIOSITIES_MASS_TRAFFIC",
    "CHANNEL_C_MOTIVATION_DISCIPLINE_RETENTION",
}

def _blocked_status_tokens() -> set[str]:
    return {
        "CONTENT" + "_CREATED",
        "DRAFT" + "_CREATED",
        "READY" + "_TO_" + "PUBLISH",
        "PROMPT" + "_EXECUTED",
        "SCRIPT" + "_EXECUTED",
        "ASSET" + "_CREATED",
        "PUBLISHED",
    }

PRODUCTIVE_STATUSES = _blocked_status_tokens()

def validate_generation_candidate_schema(candidate: dict) -> dict:
    missing = [field for field in REQUIRED_FIELDS if field not in candidate]
    empty = [field for field in REQUIRED_FIELDS if field in candidate and candidate.get(field) in ("", None, [], {})]
    if missing or empty:
        return {"status": "BLOCK", "reason": "GENERATION_CANDIDATE_SCHEMA_INVALID", "missing": missing, "empty": empty}

    if not re.match(r"^QG-\d{8}-\d{6}-[A-F0-9]{8}$", str(candidate["queue_item_id"])):
        return {"status": "BLOCK", "reason": "INVALID_QUEUE_ITEM_ID"}

    if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", str(candidate["created_at_utc"])):
        return {"status": "BLOCK", "reason": "INVALID_CREATED_AT_UTC"}

    if candidate["channel_id"] not in VALID_CHANNELS:
        return {"status": "BLOCK", "reason": "UNKNOWN_CHANNEL"}

    trace = candidate.get("traceability", {})
    required_trace = {
        "construction_core_ref": "CLOSED_VALIDATED",
        "strategy_foundation_ref": "CLOSED_VALIDATED",
        "prompt_governance_ref": "CLOSED_VALIDATED",
        "queue_governance_ref": "CLOSED_VALIDATED",
    }
    bad_trace = {key: trace.get(key) for key, expected in required_trace.items() if trace.get(key) != expected}
    if bad_trace:
        return {"status": "BLOCK", "reason": "TRACEABILITY_NOT_CLOSED_VALIDATED", "bad_trace": bad_trace}

    if candidate.get("generation_governance_status") in PRODUCTIVE_STATUSES:
        return {"status": "BLOCK", "reason": "PRODUCTIVE_STATUS_NOT_ALLOWED"}

    return {"status": "PASS", "reason": "GENERATION_CANDIDATE_SCHEMA_VALID"}
