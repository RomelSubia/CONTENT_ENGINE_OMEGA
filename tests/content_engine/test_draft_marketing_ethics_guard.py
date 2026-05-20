from content_engine.content_drafting_governance import inspect_marketing_ethics

def test_ethical_structure_allowed():
    result = inspect_marketing_ethics("estructura de persuasión ética")
    assert result["blocked"] is False

def test_false_scarcity_blocks():
    result = inspect_marketing_ethics("usar escasez falsa para presionar")
    assert result["blocked"] is True
