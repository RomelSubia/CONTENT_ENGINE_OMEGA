from content_engine.content_drafting_governance import inspect_sensitive_human_field

def test_email_blocks_in_human_field():
    assert inspect_sensitive_human_field("contacto user@example.com")["blocked"] is True

def test_technical_id_clear():
    assert inspect_sensitive_human_field("draft-candidate-001")["blocked"] is False
