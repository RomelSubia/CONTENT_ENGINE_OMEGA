from content_engine.content_drafting_governance import inspect_boundary_text

def test_boundary_clear_for_governance_text():
    assert inspect_boundary_text("governance metadata only")["blocked"] is False

def test_publish_command_blocks():
    assert inspect_boundary_text("please publish this campaign")["blocked"] is True

def test_queue_mutation_blocks():
    assert inspect_boundary_text("queue write this item")["blocked"] is True
