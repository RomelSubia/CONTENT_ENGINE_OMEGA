from content_engine.content_drafting_governance import inspect_publishability

def test_low_publishability_allowed_for_review_only():
    result = inspect_publishability("metadata for campaign review")
    assert result["blocked"] is False
    assert result["final_output_allowed"] is False

def test_high_publishability_blocks():
    result = inspect_publishability("caption final con CTA listo para post")
    assert result["blocked"] is True
    assert result["publishability_score"] >= 70
