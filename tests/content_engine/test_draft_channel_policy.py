import pytest
from content_engine.content_drafting_governance import get_supported_domains, validate_channel_or_domain

def test_required_domains_present():
    domains = get_supported_domains()
    for key in ["finca_san_mateo", "cacao", "arriendos", "bravi", "bramviss", "websites"]:
        assert key in domains

def test_unknown_domain_blocks():
    with pytest.raises(ValueError):
        validate_channel_or_domain("unknown-domain")
