import pytest
from content_engine.content_drafting_governance import get_supported_domains, validate_channel_or_domain

def test_required_domains_present():
    domains = get_supported_domains()
    for key in ["finca_san_mateo", "cacao", "arriendos", "bravi", "bramviss", "websites"]:
        assert key in domains

def test_unknown_domain_blocks():
    with pytest.raises(ValueError):
        validate_channel_or_domain("unknown-domain")


def test_supported_domains_expose_digital_channel_aliases_for_validation_contract():
    domains = get_supported_domains()
    if isinstance(domains, dict):
        domain_ids = set(domains.keys())
    else:
        domain_ids = set(domains)

    assert "digital_a" in domain_ids
    assert "digital_b" in domain_ids
    assert "digital_c" in domain_ids
    assert "digital_d" in domain_ids
    assert "digital_channel_a" in domain_ids
    assert "digital_channel_b" in domain_ids
    assert "digital_channel_c" in domain_ids
    assert "digital_channel_d" in domain_ids
