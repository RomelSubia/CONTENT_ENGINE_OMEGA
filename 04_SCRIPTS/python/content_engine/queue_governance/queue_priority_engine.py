from __future__ import annotations

from .queue_failure_policy import PASS, BLOCK

PRIORITY_BANDS = ("LOW", "MEDIUM", "HIGH", "BLOCKED")


def calculate_priority(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {"status": BLOCK, "reason": "QUEUE_SCHEMA_VERSION_INVALID", "priority_score": 0, "priority_band": "BLOCKED"}

    score = 0
    if payload.get("pillar_id"):
        score += 20
    if payload.get("audience_profile_id"):
        score += 20
    if payload.get("content_intent"):
        score += 20
    if payload.get("evidence_status") == "COMPLETE":
        score += 20
    if payload.get("risk_level") in ("CRITICAL_SECURITY_BLOCK", "CRITICAL_EXECUTION_BLOCK", "HIGH_POLICY_BLOCK"):
        return {
            "status": BLOCK,
            "reason": "QUEUE_PRIORITY_DOES_NOT_AUTHORIZE_EXECUTION",
            "priority_score": score,
            "priority_band": "BLOCKED",
            "generation_allowed": False,
            "publishing_allowed": False,
            "queue_write_allowed": False,
        }

    band = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return {
        "status": PASS,
        "priority_score": score,
        "priority_band": band,
        "generation_allowed": False,
        "publishing_allowed": False,
        "queue_write_allowed": False,
    }


def validate_priority_output(result: dict) -> dict:
    if result.get("generation_allowed") is not False:
        return {"status": BLOCK, "reason": "QUEUE_PRIORITY_DOES_NOT_AUTHORIZE_EXECUTION"}
    if result.get("publishing_allowed") is not False:
        return {"status": BLOCK, "reason": "QUEUE_PRIORITY_DOES_NOT_AUTHORIZE_EXECUTION"}
    if result.get("queue_write_allowed") is not False:
        return {"status": BLOCK, "reason": "QUEUE_PRIORITY_DOES_NOT_AUTHORIZE_EXECUTION"}
    if result.get("priority_band") not in PRIORITY_BANDS:
        return {"status": BLOCK, "reason": "QUEUE_PRIORITY_DOES_NOT_AUTHORIZE_EXECUTION"}
    return {"status": PASS, "reason": "PRIORITY_OUTPUT_VALIDATED"}
