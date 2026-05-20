from content_engine.content_drafting_governance import inspect_domain_contamination

def test_domain_contamination_clear():
    result = inspect_domain_contamination("finca_san_mateo", "evento familiar en la finca")
    assert result["blocked"] is False

def test_domain_contamination_blocks():
    result = inspect_domain_contamination("bravi", "cultivo de cacao de origen")
    assert result["blocked"] is True
