from content_engine.content_drafting_governance import assert_hard_false_permissions, get_drafting_governance_state

def test_state_hard_false_permissions():
    state = get_drafting_governance_state()
    assert state["draft_creation_allowed_now"] is False
    assert state["content_generation_allowed_now"] is False
    assert state["queue_write_allowed_now"] is False
    assert state["publishing_allowed_now"] is False
    assert state["automation_allowed_now"] is False
    assert assert_hard_false_permissions(state) is True

def test_state_next_step_post_build_audit():
    assert get_drafting_governance_state()["next_safe_step"] == "CONTENT_ENGINE_CONTENT_DRAFTING_GOVERNANCE_CORE_POST_BUILD_AUDIT"
