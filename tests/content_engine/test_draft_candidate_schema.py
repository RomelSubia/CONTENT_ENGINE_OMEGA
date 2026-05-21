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


def test_validate_draft_candidate_accepts_digital_channel_aliases_as_canonical_domains():
    base_payload = {
        "draft_candidate_id": "draft-schema-alias-test",
        "channel_or_domain_id": "finca_san_mateo",
        "monetization_intent": "booking",
        "communication_intent": "booking",
        "audience_profile": "families",
        "offer_or_value_proposition": "event review",
        "campaign_or_growth_context": "awareness",
        "expected_metric_metadata": {"metric": "qualified inquiries"},
        "learning_objective": "learn demand",
        "growth_decision_context": "campaign test",
        "maturity_level": 0,
        "evidence_refs": ["ev-schema-alias-test"],
        "traceability_refs": ["tr-schema-alias-test"],
    }

    aliases = {
        "digital_channel_a": "digital_a",
        "digital_channel_b": "digital_b",
        "digital_channel_c": "digital_c",
        "digital_channel_d": "digital_d",
    }

    for alias, canonical in aliases.items():
        payload = dict(base_payload)
        payload["draft_candidate_id"] = f"draft-schema-alias-test-{alias}"
        payload["channel_or_domain_id"] = alias

        result = validate_draft_candidate(payload)

        assert result["status"] == "PASS"
        assert result.get("channel_or_domain_id") in {alias, canonical} or result.get("canonical_channel_or_domain_id") == canonical
