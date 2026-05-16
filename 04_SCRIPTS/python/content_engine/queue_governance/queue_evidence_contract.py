from __future__ import annotations

from .queue_failure_policy import PASS, BLOCK

REQUIRED_EVIDENCE_FIELDS = (
    "channel_id",
    "pillar_id",
    "audience_profile_id",
    "content_intent",
    "risk_level",
    "traceability",
)


def validate_queue_evidence(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {"status": BLOCK, "reason": "QUEUE_SCHEMA_VERSION_INVALID"}
    missing = [field for field in REQUIRED_EVIDENCE_FIELDS if not payload.get(field)]
    if missing:
        return {
            "status": BLOCK,
            "reason": "MEDIUM_GOVERNANCE_BLOCK",
            "missing_evidence": missing,
            "queue_write_performed": False,
        }
    return {"status": PASS, "reason": "QUEUE_EVIDENCE_VALIDATED"}


def build_evidence_requirement_report(payload: dict) -> dict:
    validation = validate_queue_evidence(payload)
    return {
        "status": validation.get("status"),
        "required_fields": list(REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": validation.get("missing_evidence", []),
        "queue_write_performed": False,
        "content_generation_started": False,
    }
