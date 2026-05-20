from __future__ import annotations

from .draft_channel_policy import validate_channel_or_domain
from .draft_failure_policy import fail_closed_result

REQUIRED_FIELDS = [
    "draft_candidate_id",
    "channel_or_domain_id",
    "monetization_intent",
    "communication_intent",
    "audience_profile",
    "campaign_or_growth_context",
    "expected_metric_metadata",
    "learning_objective",
    "growth_decision_context",
    "maturity_level",
    "evidence_refs",
    "traceability_refs",
]

COMMERCIAL_INTENTS = {"sale", "booking", "lead_generation", "offer", "conversion"}


def validate_draft_candidate(payload: dict[str, object]) -> dict[str, object]:
    missing = [field for field in REQUIRED_FIELDS if payload.get(field) in (None, "", [])]
    if payload.get("communication_intent") in COMMERCIAL_INTENTS and not payload.get("offer_or_value_proposition"):
        missing.append("offer_or_value_proposition")

    if missing:
        return fail_closed_result("DRAFT_CANDIDATE_SCHEMA_MISSING_FIELDS", extra={"missing": sorted(set(missing))})

    try:
        validate_channel_or_domain(str(payload["channel_or_domain_id"]))
    except ValueError as exc:
        return fail_closed_result("DRAFT_CANDIDATE_SCHEMA_UNSUPPORTED_DOMAIN", extra={"error": str(exc)})

    return {
        "status": "PASS",
        "draft_candidate_id": payload["draft_candidate_id"],
        "channel_or_domain_id": payload["channel_or_domain_id"],
        "human_review_required": True,
        "final_output_allowed": False,
        "draft_creation_allowed": False,
        "content_generation_allowed": False,
        "queue_write_allowed": False,
        "publishing_allowed": False,
        "automation_allowed": False,
    }
