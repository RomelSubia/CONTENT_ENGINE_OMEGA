from __future__ import annotations

SUPPORTED_DOMAINS = {
    "finca_san_mateo": {"kind": "business_domain", "tone": "warm_commercial"},
    "cacao": {"kind": "agro_commercial_domain", "tone": "educational_origin"},
    "arriendos": {"kind": "real_estate_domain", "tone": "clear_trust"},
    "bravi": {"kind": "business_domain", "tone": "professional"},
    "bramviss": {"kind": "industrial_business_domain", "tone": "technical_commercial"},
    "digital_a": {"kind": "digital_channel", "tone": "conversion"},
    "digital_b": {"kind": "digital_channel", "tone": "mass_reach"},
    "digital_c": {"kind": "digital_channel", "tone": "discipline_retention"},
    "digital_d": {"kind": "digital_channel", "tone": "tech_authority"},
    "social_networks": {"kind": "platform_group", "tone": "platform_specific"},
    "websites": {"kind": "web_presence", "tone": "trust_conversion"},
    "future_business_or_brand": {"kind": "future_domain", "tone": "to_be_defined"},
}


def get_supported_domains() -> dict[str, dict[str, str]]:
    return dict(SUPPORTED_DOMAINS)


def validate_channel_or_domain(channel_or_domain_id: str) -> dict[str, str]:
    if channel_or_domain_id not in SUPPORTED_DOMAINS:
        raise ValueError(f"unsupported channel_or_domain_id: {channel_or_domain_id}")
    return dict(SUPPORTED_DOMAINS[channel_or_domain_id])
