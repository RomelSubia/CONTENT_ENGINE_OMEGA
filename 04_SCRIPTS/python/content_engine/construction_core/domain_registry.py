from __future__ import annotations

from typing import Any

DOMAINS = [
    "governance",
    "construction",
    "strategy",
    "prompts",
    "scripts",
    "assets",
    "queue",
    "metrics",
    "monetization",
    "publishing_preparation",
    "audit",
]


def build_domain_registry() -> dict[str, Any]:
    return {
        "status": "PASS",
        "domain_count": len(DOMAINS),
        "domains": [{"id": domain, "execution_allowed_now": False} for domain in DOMAINS],
    }


def validate_domain_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = registry or build_domain_registry()
    domains = registry.get("domains", [])
    ids = [item.get("id") for item in domains]
    missing = [domain for domain in DOMAINS if domain not in ids]
    unsafe = [item.get("id") for item in domains if item.get("execution_allowed_now") is not False]
    return {
        "status": "PASS" if not missing and not unsafe else "BLOCK",
        "missing": missing,
        "unsafe": unsafe,
    }
