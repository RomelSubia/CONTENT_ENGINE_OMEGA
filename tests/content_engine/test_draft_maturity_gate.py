from content_engine.content_drafting_governance import evaluate_maturity_gate

def test_level_zero_blocks_promotion():
    result = evaluate_maturity_gate({"maturity_level": 0, "evidence_refs": []})
    assert result["promotion_allowed"] is False
    assert result["draft_creation_allowed"] is False

def test_evidence_only_promotes_to_review_not_autonomy():
    result = evaluate_maturity_gate({"maturity_level": 1, "evidence_refs": ["ev"], "metrics_ready": True, "recovery_ready": True})
    assert result["promotion_allowed"] is True
    assert result["autonomy_escalation_allowed"] is False
