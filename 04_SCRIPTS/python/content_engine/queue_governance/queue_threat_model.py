from __future__ import annotations

from .queue_failure_policy import PASS, BLOCK
from .queue_sensitive_data_guard import validate_payload_safety
from .queue_boundary_guard import detect_soft_execution_trigger, detect_human_approval_bypass

THREATS = {
    "T01_MALICIOUS_INPUT": "malicious input",
    "T02_PATH_TRAVERSAL": "path traversal",
    "T03_PROMPT_INJECTION": "prompt injection",
    "T04_POLICY_OVERRIDE": "policy override",
    "T05_STATE_ESCALATION": "state escalation",
    "T06_FAKE_READINESS": "fake readiness",
    "T07_FAKE_PRIORITY": "fake priority",
    "T08_CHANNEL_CONTAMINATION": "channel contamination",
    "T09_QUEUE_PERSISTENCE_ATTEMPT": "queue persistence attempt",
    "T10_HIDDEN_AUTOMATION_TRIGGER": "hidden automation trigger",
    "T11_SECRET_LEAKAGE": "secret leakage",
    "T12_PII_LEAKAGE": "pii leakage",
    "T13_ID_COLLISION": "id collision",
    "T14_TIMESTAMP_TAMPERING": "timestamp tampering",
    "T15_MANIFEST_SPOOFING": "manifest spoofing",
    "T16_SEAL_SPOOFING": "seal spoofing",
    "T17_HUMAN_APPROVAL_BYPASS": "human approval bypass",
    "T18_SOFT_EXECUTION_REQUEST": "soft execution request",
    "T19_EXTERNAL_API_IMPORT_ATTEMPT": "external api import attempt",
    "T20_METRIC_BASED_AUTO_DECISION_ATTEMPT": "metric based auto decision attempt",
}

RISK_LEVELS = (
    "LOW_REVIEW_BLOCK",
    "MEDIUM_GOVERNANCE_BLOCK",
    "HIGH_POLICY_BLOCK",
    "CRITICAL_EXECUTION_BLOCK",
    "CRITICAL_SECURITY_BLOCK",
)


def build_queue_threat_model() -> dict:
    return {
        "status": PASS,
        "threat_count": len(THREATS),
        "threats": THREATS,
        "risk_levels": list(RISK_LEVELS),
    }


def validate_threat_model() -> dict:
    model = build_queue_threat_model()
    if model["threat_count"] < 20:
        return {"status": BLOCK, "reason": "QUEUE_FAILURE_POLICY_REQUIRED"}
    return {"status": PASS, "reason": "THREAT_MODEL_VALIDATED"}


def _human_intent_text(payload: dict) -> str:
    return " ".join(
        str(payload.get(key, ""))
        for key in ("idea_title", "idea_summary", "content_intent", "blocked_reason")
    ).lower()


def classify_queue_risk(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {
            "status": BLOCK,
            "risk_level": "HIGH_POLICY_BLOCK",
            "reason": "QUEUE_SCHEMA_VERSION_INVALID",
            "dominates_priority": True,
            "dominates_readiness": True,
        }

    text = _human_intent_text(payload)

    for check in (detect_soft_execution_trigger(text), detect_human_approval_bypass(text)):
        if check.get("status") == BLOCK:
            return {
                "status": BLOCK,
                "risk_level": "CRITICAL_EXECUTION_BLOCK",
                "reason": check.get("reason"),
                "dominates_priority": True,
                "dominates_readiness": True,
            }

    safety = validate_payload_safety(payload)
    if safety.get("status") == BLOCK:
        return {
            "status": BLOCK,
            "risk_level": "CRITICAL_SECURITY_BLOCK",
            "reason": safety.get("reason"),
            "dominates_priority": True,
            "dominates_readiness": True,
        }

    return {
        "status": PASS,
        "risk_level": "LOW_REVIEW_BLOCK",
        "reason": "NO_CRITICAL_RISK_DETECTED",
        "dominates_priority": False,
        "dominates_readiness": False,
    }
