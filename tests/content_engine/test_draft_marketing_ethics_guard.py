from content_engine.content_drafting_governance import inspect_marketing_ethics

def test_ethical_structure_allowed():
    result = inspect_marketing_ethics("estructura de persuasión ética")
    assert result["blocked"] is False

def test_false_scarcity_blocks():
    result = inspect_marketing_ethics("usar escasez falsa para presionar")
    assert result["blocked"] is True


def test_marketing_ethics_blocks_false_urgency_phrases_spanish_and_english():
    phrases = [
        "urgencia falsa",
        "crear urgencia falsa",
        "usar urgencia falsa",
        "presionar con urgencia falsa",
        "falsa urgencia",
        "crear falsa urgencia",
        "usar falsa urgencia",
        "false urgency",
        "fake urgency",
        "artificial urgency",
        "manufactured urgency",
        "create false urgency",
        "use false urgency",
        "pressure with false urgency",
    ]

    for phrase in phrases:
        result = inspect_marketing_ethics(phrase)
        assert result["blocked"] is True
        assert result["draft_creation_allowed"] is False
        assert result["content_generation_allowed"] is False
        assert result["final_output_allowed"] is False
