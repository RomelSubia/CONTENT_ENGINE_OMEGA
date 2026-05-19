"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


EVIDENCE_STATES = {"EVIDENCE_MISSING", "EVIDENCE_PARTIAL", "EVIDENCE_REVIEW_READY", "EVIDENCE_STRONG"}
REQUIRED_EVIDENCE = [
    "channel_fit_review",
    "audience_fit_review",
    "pillar_fit_review",
    "policy_review",
    "risk_review",
    "traceability_review",
    "sensitive_data_review",
    "human_safety_review",
]

def validate_generation_evidence(candidate: dict) -> dict:
    evidence_status = candidate.get("evidence_status")
    if evidence_status not in EVIDENCE_STATES:
        return {"status": "BLOCK", "reason": "UNKNOWN_EVIDENCE_STATUS"}
    if evidence_status == "EVIDENCE_MISSING":
        return {"status": "BLOCK", "reason": "GENERATION_BLOCKED_BY_EVIDENCE", "required_evidence": REQUIRED_EVIDENCE}
    return {"status": "PASS", "reason": "EVIDENCE_READY_FOR_REVIEW_ONLY", "required_evidence": REQUIRED_EVIDENCE}
