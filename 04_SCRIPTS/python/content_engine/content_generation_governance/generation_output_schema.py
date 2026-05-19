"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


from .generation_governance_state import HARD_FALSE_KEYS

REQUIRED_OUTPUT_FIELDS = (
    "status",
    "generation_governance_status",
    "reason",
    "risk_level",
    "human_review_required",
    "blocked_operations",
    "required_evidence",
    "required_reviews",
    "traceability_ref",
    "layer_mode",
    "generation_execution_allowed_now",
) + HARD_FALSE_KEYS

SAFE_REVIEW_NAMES = {
    "policy_review",
    "risk_review",
    "channel_fit_review",
    "traceability_review",
    "sensitive_data_review",
    "human_safety_review",
    "evidence_review",
    "technical_accuracy_review",
    "claim_review",
    "tone_review",
    "source_review",
    "fact_check_review",
    "tool_claim_review",
    "conversion_ethics_review",
    "audience_fit_review",
    "pillar_fit_review",
}

UNSAFE_REVIEW_NAME_FRAGMENTS = (
    "publish",
    "generation_allowed",
    "draft_ready",
    "ready_to_publish",
    "content_ready",
    "generation_approval",
    "draft_approval",
)

def validate_required_reviews(required_reviews: list[str]) -> dict:
    unsafe = [
        review for review in required_reviews
        if any(fragment in review for fragment in UNSAFE_REVIEW_NAME_FRAGMENTS)
    ]
    if unsafe:
        return {"status": "BLOCK", "reason": "UNSAFE_REQUIRED_REVIEW_NAME", "unsafe": unsafe}
    unknown = [review for review in required_reviews if review not in SAFE_REVIEW_NAMES]
    if unknown:
        return {"status": "BLOCK", "reason": "UNKNOWN_REQUIRED_REVIEW_NAME", "unknown": unknown}
    return {"status": "PASS", "reason": "REQUIRED_REVIEWS_SAFE"}

def make_generation_output(
    *,
    status: str,
    generation_governance_status: str,
    reason: str,
    risk_level: str,
    blocked_operations: list[str] | None = None,
    required_evidence: list[str] | None = None,
    required_reviews: list[str] | None = None,
    traceability_ref: dict | None = None,
) -> dict:
    output = {
        "status": status,
        "generation_governance_status": generation_governance_status,
        "reason": reason,
        "risk_level": risk_level,
        "human_review_required": True,
        "blocked_operations": blocked_operations or [],
        "required_evidence": required_evidence or [],
        "required_reviews": required_reviews or ["policy_review", "risk_review", "traceability_review"],
        "traceability_ref": traceability_ref or {},
        "layer_mode": "GOVERNANCE_ONLY",
        "generation_execution_allowed_now": False,
    }
    for key in HARD_FALSE_KEYS:
        output[key] = False
    return output

def validate_generation_output_schema(output: dict) -> dict:
    missing = [field for field in REQUIRED_OUTPUT_FIELDS if field not in output]
    if missing:
        return {"status": "BLOCK", "reason": "OUTPUT_SCHEMA_MISSING_FIELDS", "missing": missing}
    if output.get("layer_mode") != "GOVERNANCE_ONLY":
        return {"status": "BLOCK", "reason": "LAYER_MODE_NOT_GOVERNANCE_ONLY"}
    if output.get("human_review_required") is not True:
        return {"status": "BLOCK", "reason": "HUMAN_REVIEW_REQUIRED_MUST_ALWAYS_BE_TRUE"}
    false_violations = [key for key in HARD_FALSE_KEYS if output.get(key) is not False]
    if output.get("generation_execution_allowed_now") is not False:
        false_violations.append("generation_execution_allowed_now")
    if false_violations:
        return {"status": "BLOCK", "reason": "OUTPUT_HARD_FALSE_VIOLATION", "false_violations": false_violations}
    reviews = validate_required_reviews(list(output.get("required_reviews", [])))
    if reviews["status"] != "PASS":
        return reviews
    return {"status": "PASS", "reason": "OUTPUT_SCHEMA_VALID"}
