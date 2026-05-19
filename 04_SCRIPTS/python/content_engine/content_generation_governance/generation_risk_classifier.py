"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


from .generation_boundary_guard import classify_generation_boundary_text
from .generation_sensitive_data_guard import validate_sensitive_data_field_scope
from .generation_channel_policy import validate_channel_specific_policy
from .generation_duplication_guard import validate_duplication_governance

def classify_generation_risk(candidate: dict) -> dict:
    text = f"{candidate.get('idea_title','')} {candidate.get('idea_summary','')} {candidate.get('content_intent','')}"
    boundary = classify_generation_boundary_text(text)
    if boundary["status"] == "BLOCK":
        reason = boundary["reason"]
        if "PUBLICATION" in reason:
            return {"status": "BLOCK", "risk_level": "CRITICAL_PUBLICATION_BLOCK", "reason": reason}
        if "AUTOMATION" in reason:
            return {"status": "BLOCK", "risk_level": "CRITICAL_AUTOMATION_BLOCK", "reason": reason}
        return {"status": "BLOCK", "risk_level": "CRITICAL_EXECUTION_BLOCK", "reason": reason}

    sensitive = validate_sensitive_data_field_scope(candidate)
    if sensitive["status"] == "BLOCK":
        return {"status": "BLOCK", "risk_level": "CRITICAL_SECURITY_BLOCK", "reason": sensitive["reason"]}

    text_lower = text.lower()
    if any(x in text_lower for x in ["disciplina tóxica", "culpa extrema", "valor personal"]):
        return {"status": "BLOCK", "risk_level": "SAFETY_RISK", "reason": "SAFETY_RISK_BLOCK"}

    channel = validate_channel_specific_policy(candidate)
    if channel["status"] == "BLOCK":
        return {"status": "BLOCK", "risk_level": "CHANNEL_CONTAMINATION_RISK", "reason": channel["reason"]}

    duplicate = validate_duplication_governance(candidate)
    if duplicate["status"] == "BLOCK":
        return {"status": "BLOCK", "risk_level": "DUPLICATION_RISK", "reason": duplicate["reason"]}

    if candidate.get("evidence_status") in ("EVIDENCE_MISSING", "PARTIAL"):
        return {"status": "PASS", "risk_level": "LOW_EVIDENCE_RISK", "reason": "LOW_EVIDENCE_REVIEW_REQUIRED"}

    return {"status": "PASS", "risk_level": "LOW_REVIEW_BLOCK", "reason": "LOW_RISK_STILL_REQUIRES_REVIEW"}
