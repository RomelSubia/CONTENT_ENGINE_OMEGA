from __future__ import annotations

from typing import Any

from .channel_registry import get_channels

REQUIRED_FIELDS = [
    "channel_id",
    "channel_name",
    "core_purpose",
    "primary_audience",
    "secondary_audience",
    "allowed_tone",
    "blocked_tone",
    "allowed_content_intent",
    "blocked_content_intent",
    "allowed_pillars",
    "blocked_pillars",
    "monetization_future",
    "authority_level",
    "risk_profile",
    "separation_rules",
    "quality_requirements",
]


def build_identity_contracts() -> dict[str, dict[str, Any]]:
    contracts: dict[str, dict[str, Any]] = {}
    for channel_id, data in get_channels().items():
        contracts[channel_id] = {
            "channel_id": channel_id,
            "channel_name": data["channel_name"],
            "core_purpose": data["core_purpose"],
            "primary_audience": data["primary_audience"],
            "secondary_audience": "audiencia secundaria futura no personalizada",
            "allowed_tone": list(data["allowed_tone"]),
            "blocked_tone": list(data["blocked_tone"]),
            "allowed_content_intent": ["educar", "atraer", "posicionar"],
            "blocked_content_intent": ["publicar ahora", "vender agresivamente", "prometer resultados no verificados"],
            "allowed_pillars": ["PILLARS_DEFINED_BY_CHANNEL_REGISTRY"],
            "blocked_pillars": ["CROSS_CHANNEL_PILLARS_WITHOUT_BRIDGE_RULE"],
            "monetization_future": "futura, no ejecutable",
            "authority_level": "governed",
            "risk_profile": data["risk_profile"],
            "separation_rules": ["usar ID canónico", "no mezclar sin regla puente"],
            "quality_requirements": ["alineación de canal", "evidencia", "no ejecución"],
        }
    return contracts


def validate_identity_contracts(contracts: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    contracts = contracts or build_identity_contracts()
    missing: dict[str, list[str]] = {}
    for channel_id, payload in contracts.items():
        absent = [field for field in REQUIRED_FIELDS if field not in payload or payload.get(field) in (None, "", [])]
        if absent:
            missing[channel_id] = absent
    return {"status": "PASS" if not missing else "BLOCK", "missing": missing}
