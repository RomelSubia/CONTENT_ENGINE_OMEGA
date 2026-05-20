from content_engine.content_drafting_governance import validate_draft_candidate

BASE = {
    "draft_candidate_id": "draft-candidate-001",
    "channel_or_domain_id": "finca_san_mateo",
    "monetization_intent": "booking",
    "communication_intent": "booking",
    "audience_profile": "families",
    "offer_or_value_proposition": "event space review",
    "campaign_or_growth_context": "awareness",
    "expected_metric_metadata": {"metric": "qualified inquiries"},
    "learning_objective": "learn demand",
    "growth_decision_context": "campaign test",
    "maturity_level": 0,
    "evidence_refs": ["ev-1"],
    "traceability_refs": ["tr-1"],
}

def test_valid_candidate_requires_human_review():
    result = validate_draft_candidate(dict(BASE))
    assert result["status"] == "PASS"
    assert result["human_review_required"] is True
    assert result["final_output_allowed"] is False

def test_missing_required_field_fails_closed():
    payload = dict(BASE)
    payload.pop("channel_or_domain_id")
    result = validate_draft_candidate(payload)
    assert result["status"] == "FAILED_BLOCKED"
    assert result["draft_creation_performed"] is False
