from content_engine.content_drafting_governance import inspect_near_final_text

def test_near_final_clear():
    assert inspect_near_final_text("conceptual structure only")["blocked"] is False

def test_final_caption_blocks():
    assert inspect_near_final_text("caption final para publicar")["blocked"] is True
