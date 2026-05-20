from content_engine.content_drafting_governance import classify_monetization_claim_risk

def test_safe_monetization_metadata_requires_review_not_block():
    result = classify_monetization_claim_risk("objetivo de conversión medible")
    assert result["human_review_required"] is True

def test_false_income_guarantee_blocks_without_evidence():
    result = classify_monetization_claim_risk("ingresos garantizados para todos")
    assert result["blocked"] is True

def test_claim_with_evidence_still_review_required():
    result = classify_monetization_claim_risk("ingresos garantizados", has_evidence=True)
    assert result["blocked"] is False
    assert result["human_review_required"] is True
