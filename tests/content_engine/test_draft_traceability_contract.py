from content_engine.content_drafting_governance import validate_traceability_contract

def test_traceability_required():
    result = validate_traceability_contract({"channel_or_domain_id": "bravi", "traceability_refs": ["tr-1"]})
    assert result["valid"] is True

def test_missing_traceability_blocks():
    result = validate_traceability_contract({"channel_or_domain_id": "bravi"})
    assert result["valid"] is False
