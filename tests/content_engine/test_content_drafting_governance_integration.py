from content_engine.content_drafting_governance import (
    get_argos_contract_hint,
    inspect_boundary_text,
    inspect_marketing_ethics,
    inspect_publishability,
    validate_draft_candidate,
)

def test_integration_safe_conceptual_payload():
    payload = {
        "draft_candidate_id": "draft-candidate-002",
        "channel_or_domain_id": "bravi",
        "monetization_intent": "lead_generation",
        "communication_intent": "lead_generation",
        "audience_profile": "industrial clients",
        "offer_or_value_proposition": "technical service review",
        "campaign_or_growth_context": "authority",
        "expected_metric_metadata": {"metric": "lead quality"},
        "learning_objective": "learn response",
        "growth_decision_context": "B2B test",
        "maturity_level": 0,
        "evidence_refs": ["ev-1"],
        "traceability_refs": ["tr-1"],
    }
    result = validate_draft_candidate(payload)
    assert result["status"] == "PASS"
    assert inspect_boundary_text("governance metadata only")["blocked"] is False
    assert inspect_marketing_ethics("ethical structure")["blocked"] is False
    assert inspect_publishability("metadata only")["final_output_allowed"] is False
    assert get_argos_contract_hint()["argos_dependency"] is False
