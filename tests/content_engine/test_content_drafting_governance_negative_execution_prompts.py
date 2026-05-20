from content_engine.content_drafting_governance import inspect_boundary_text, inspect_near_final_text, inspect_publishability

def test_negative_publish_prompt_blocks():
    assert inspect_boundary_text("publicar ahora en redes")["blocked"] is True

def test_negative_script_execution_blocks():
    assert inspect_boundary_text("execute script to publish")["blocked"] is True

def test_negative_near_final_blocks():
    assert inspect_near_final_text("guion final listo")["blocked"] is True

def test_negative_publishability_blocks():
    assert inspect_publishability("caption final CTA post listo")["blocked"] is True
