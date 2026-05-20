from content_engine.content_drafting_governance import validate_evidence_contract

def test_missing_evidence_blocks_when_required():
    result = validate_evidence_contract({"evidence_refs": []}, claim_requires_evidence=True)
    assert result["blocked"] is True

def test_evidence_valid_when_present():
    result = validate_evidence_contract({"evidence_refs": ["ev-1"]}, claim_requires_evidence=True)
    assert result["valid"] is True
    assert result["blocked"] is False
