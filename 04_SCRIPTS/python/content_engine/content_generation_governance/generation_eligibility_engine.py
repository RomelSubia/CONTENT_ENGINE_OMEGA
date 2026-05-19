"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


from .generation_candidate_schema import validate_generation_candidate_schema
from .generation_risk_classifier import classify_generation_risk
from .generation_output_schema import make_generation_output, validate_generation_output_schema

def classify_generation_eligibility(candidate: dict) -> dict:
    schema = validate_generation_candidate_schema(candidate)
    if schema["status"] != "PASS":
        output = make_generation_output(
            status="BLOCK",
            generation_governance_status="GENERATION_BLOCKED",
            reason=schema["reason"],
            risk_level="SCHEMA_BLOCK",
            blocked_operations=["content_generation", "draft_creation", "publishing", "automation"],
            traceability_ref=candidate.get("traceability", {}),
        )
        return output

    risk = classify_generation_risk(candidate)
    if risk["status"] == "BLOCK":
        output = make_generation_output(
            status="BLOCK",
            generation_governance_status="GENERATION_BLOCKED",
            reason=risk["reason"],
            risk_level=risk["risk_level"],
            blocked_operations=["content_generation", "draft_creation", "publishing", "automation"],
            traceability_ref=candidate.get("traceability", {}),
        )
        return output

    output = make_generation_output(
        status="PASS",
        generation_governance_status="GENERATION_HUMAN_REVIEW_REQUIRED",
        reason="GENERATION_GOVERNANCE_REVIEW_REQUIRED",
        risk_level=risk["risk_level"],
        blocked_operations=["content_generation", "draft_creation", "publishing", "automation"],
        required_evidence=["policy_review", "risk_review", "traceability_review", "sensitive_data_review"],
        required_reviews=["policy_review", "risk_review", "traceability_review", "sensitive_data_review"],
        traceability_ref=candidate.get("traceability", {}),
    )
    validation = validate_generation_output_schema(output)
    if validation["status"] != "PASS":
        return make_generation_output(
            status="BLOCK",
            generation_governance_status="GENERATION_BLOCKED",
            reason=validation["reason"],
            risk_level="OUTPUT_SCHEMA_BLOCK",
        )
    return output
