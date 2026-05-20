from content_engine.content_drafting_governance import get_argos_contract_hint

def test_argos_metadata_only():
    hint = get_argos_contract_hint()
    assert hint["compatibility_mode"] == "METADATA_ONLY"
    assert hint["argos_dependency"] is False
    assert hint["cross_imports_allowed"] is False
    assert hint["argos_can_bypass_gates"] is False
