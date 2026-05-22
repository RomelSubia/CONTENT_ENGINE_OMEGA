from __future__ import annotations

from .runtime_contracts import PASS, SUPPORTED_DOMAINS
from .runtime_failure_policy import fail_closed

def validate_domain_isolation(domain: str, expected_domain: str | None = None) -> dict[str, object]:
    if domain not in SUPPORTED_DOMAINS:
        return fail_closed("UNSUPPORTED_DOMAIN_OR_CHANNEL")
    if expected_domain is not None and domain != expected_domain:
        return fail_closed("UNSUPPORTED_DOMAIN_OR_CHANNEL")
    return {
        "status": PASS,
        "domain_context_must_match": True,
        "cross_domain_contamination_allowed": False,
        "brand_voice_mixing_allowed": False,
        "campaign_context_mixing_allowed": False,
    }
