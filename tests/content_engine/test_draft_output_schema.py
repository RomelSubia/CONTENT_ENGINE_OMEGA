from content_engine.content_drafting_governance import make_governance_output

def test_output_schema_hard_false():
    output = make_governance_output(status="PASS", reason="TEST")
    assert output["human_review_required"] is True
    assert output["final_output_allowed"] is False
    assert output["draft_creation_performed"] is False
    assert output["queue_write_performed"] is False
