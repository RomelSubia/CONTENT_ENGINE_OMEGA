"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


import re

TECHNICAL_FIELDS = {
    "schema_version",
    "queue_item_id",
    "created_at_utc",
    "channel_id",
    "pillar_id",
    "audience_profile_id",
    "risk_level",
    "evidence_status",
    "traceability",
}

HUMAN_FIELDS = {
    "idea_title",
    "idea_summary",
    "content_intent",
    "notes",
    "risk_notes",
    "review_notes",
    "blocked_reason",
    "candidate_context",
    "human_comment",
}

def _detect_sensitive_value(value: str) -> list[str]:
    text = str(value)
    detections = []
    if re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", text, re.I):
        detections.append("EMAIL")
    if re.search(r"\b(?:\+?\d[\s-]?){8,}\b", text):
        detections.append("PHONE")
    if re.search(r"[A-Z]:\\", text):
        detections.append("LOCAL_PATH")
    if re.search(r"(?i)(api[_-]?key|secret|token|password|bearer)", text):
        detections.append("SECRET_OR_TOKEN")
    if "CLIENTE_" in text or "EMPRESA_" in text:
        detections.append("REAL_OR_SYNTHETIC_ENTITY_REVIEW")
    return detections

def validate_sensitive_data_field_scope(payload: dict) -> dict:
    violations = {}
    for field, value in payload.items():
        if field in TECHNICAL_FIELDS:
            continue
        if field in HUMAN_FIELDS:
            detections = _detect_sensitive_value(str(value))
            if detections:
                violations[field] = detections
    if violations:
        return {"status": "BLOCK", "reason": "SENSITIVE_DATA_FIELD_SCOPE_BLOCK", "violations": violations}
    return {"status": "PASS", "reason": "NO_SENSITIVE_DATA_IN_HUMAN_FIELDS"}
