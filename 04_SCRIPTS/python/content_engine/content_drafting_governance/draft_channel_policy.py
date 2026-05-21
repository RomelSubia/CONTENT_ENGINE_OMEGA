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


def _cdg_original_get_supported_domains() -> dict[str, dict[str, str]]:
    return dict(SUPPORTED_DOMAINS)


def validate_channel_or_domain(channel_or_domain_id: str) -> dict[str, str]:
    if channel_or_domain_id not in SUPPORTED_DOMAINS:
        raise ValueError(f"unsupported channel_or_domain_id: {channel_or_domain_id}")
    return dict(SUPPORTED_DOMAINS[channel_or_domain_id])

# --- FINAL_CONSOLIDATED_DIGITAL_CHANNEL_ALIAS_NORMALIZATION ---
_CDG_DIGITAL_CHANNEL_ALIAS_TO_CANONICAL = {
    "digital_channel_a": "digital_a",
    "digital_channel_b": "digital_b",
    "digital_channel_c": "digital_c",
    "digital_channel_d": "digital_d",
}


def _cdg_domain_alias_payload(original_domains: object, alias: str, canonical: str) -> object:
    if isinstance(original_domains, dict) and canonical in original_domains:
        value = original_domains[canonical]
        if isinstance(value, dict):
            payload = dict(value)
            payload.setdefault("domain_id", alias)
            payload.setdefault("canonical_domain_id", canonical)
            payload.setdefault("alias_of", canonical)
            payload.setdefault("alias_normalized", True)
            return payload
        return value
    return {
        "domain_id": alias,
        "canonical_domain_id": canonical,
        "alias_of": canonical,
        "alias_normalized": True,
        "draft_creation_allowed": False,
        "content_generation_allowed": False,
        "queue_write_allowed": False,
        "publishing_allowed": False,
        "automation_allowed": False,
    }


def get_supported_domains() -> object:
    original_domains = _cdg_original_get_supported_domains()

    if isinstance(original_domains, dict):
        normalized = dict(original_domains)
        for alias, canonical in _CDG_DIGITAL_CHANNEL_ALIAS_TO_CANONICAL.items():
            normalized.setdefault(alias, _cdg_domain_alias_payload(original_domains, alias, canonical))
        return normalized

    if isinstance(original_domains, tuple):
        values = list(original_domains)
        for alias in _CDG_DIGITAL_CHANNEL_ALIAS_TO_CANONICAL:
            if alias not in values:
                values.append(alias)
        return tuple(values)

    if isinstance(original_domains, list):
        values = list(original_domains)
        for alias in _CDG_DIGITAL_CHANNEL_ALIAS_TO_CANONICAL:
            if alias not in values:
                values.append(alias)
        return values

    if isinstance(original_domains, set):
        values = set(original_domains)
        values.update(_CDG_DIGITAL_CHANNEL_ALIAS_TO_CANONICAL)
        return values

    return original_domains
# --- END FINAL_CONSOLIDATED_DIGITAL_CHANNEL_ALIAS_NORMALIZATION ---
