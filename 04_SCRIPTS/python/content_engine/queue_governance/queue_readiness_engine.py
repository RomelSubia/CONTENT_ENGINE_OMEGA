from __future__ import annotations

from .queue_failure_policy import PASS, BLOCK

READINESS_STATUSES = ("NOT_READY", "REVIEW_READY", "BLOCKED")


def calculate_readiness(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {"status": BLOCK, "reason": "QUEUE_SCHEMA_VERSION_INVALID", "readiness_score": 0, "readiness_status": "BLOCKED"}

    factors = [
        bool(payload.get("channel_id")),
        bool(payload.get("pillar_id")),
        bool(payload.get("audience_profile_id")),
        bool(payload.get("content_intent")),
        payload.get("risk_level") not in ("CRITICAL_SECURITY_BLOCK", "CRITICAL_EXECUTION_BLOCK", "HIGH_POLICY_BLOCK"),
        payload.get("evidence_status") in ("PARTIAL", "COMPLETE"),
    ]
    score = sum(1 for item in factors if item) * 15

    if payload.get("risk_level") in ("CRITICAL_SECURITY_BLOCK", "CRITICAL_EXECUTION_BLOCK", "HIGH_POLICY_BLOCK"):
        return {
            "status": BLOCK,
            "reason": "QUEUE_READINESS_DOES_NOT_AUTHORIZE_EXECUTION",
            "readiness_score": score,
            "readiness_status": "BLOCKED",
            "allowed_next": "BLOCKED",
            "generation_allowed": False,
            "publishing_allowed": False,
            "queue_write_allowed": False,
        }

    readiness = "REVIEW_READY" if score >= 75 else "NOT_READY"
    return {
        "status": PASS,
        "readiness_score": score,
        "readiness_status": readiness,
        "allowed_next": "REVIEW_ONLY",
        "generation_allowed": False,
        "publishing_allowed": False,
        "queue_write_allowed": False,
    }


def validate_readiness_output(result: dict) -> dict:
    if result.get("readiness_status") not in READINESS_STATUSES:
        return {"status": BLOCK, "reason": "QUEUE_READINESS_DOES_NOT_AUTHORIZE_EXECUTION"}
    if result.get("readiness_status") == "REVIEW_READY" and result.get("generation_allowed") is not False:
        return {"status": BLOCK, "reason": "QUEUE_REVIEW_READY_NOT_GENERATION_READY"}
    if result.get("publishing_allowed") is not False:
        return {"status": BLOCK, "reason": "QUEUE_READINESS_DOES_NOT_AUTHORIZE_EXECUTION"}
    if result.get("queue_write_allowed") is not False:
        return {"status": BLOCK, "reason": "QUEUE_READINESS_DOES_NOT_AUTHORIZE_EXECUTION"}
    return {"status": PASS, "reason": "READINESS_OUTPUT_VALIDATED"}
