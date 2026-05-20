from content_engine.content_drafting_governance import fail_closed_result

def test_fail_closed_flags():
    result = fail_closed_result("TEST_FAILURE")
    assert result["status"] == "FAILED_BLOCKED"
    assert result["draft_creation_performed"] is False
    assert result["content_generation_performed"] is False
    assert result["publishing_performed"] is False
