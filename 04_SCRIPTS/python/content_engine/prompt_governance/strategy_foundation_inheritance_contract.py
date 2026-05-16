from __future__ import annotations

from typing import Any

REQUIRED_CHANNELS = [
    "CHANNEL_A_MONEY_MINDSET_CONVERSION",
    "CHANNEL_D_AI_TECH_PERSONAL_BRAND",
    "CHANNEL_B_CURIOSITIES_MASS_TRAFFIC",
    "CHANNEL_C_MOTIVATION_DISCIPLINE_RETENTION",
]


def build_required_inheritance() -> dict[str, Any]:
    return {
        "construction_core_status": "CLOSED_VALIDATED",
        "strategy_foundation_core_status": "CLOSED_VALIDATED",
        "strategy_foundation_seal": "CONTENT_ENGINE_STRATEGY_FOUNDATION_CORE_CLOSED_VALIDATED",
        "canonical_channel_ids": list(REQUIRED_CHANNELS),
        "channel_identity_available": True,
        "pillar_registry_available": True,
        "audience_registry_available": True,
        "channel_separation_available": True,
        "boundary_rules_available": True,
    }


def validate_strategy_foundation_inheritance(evidence: dict[str, Any]) -> dict[str, Any]:
    expected = build_required_inheritance()
    failures = []
    for key, value in expected.items():
        if evidence.get(key) != value:
            failures.append(key)
    return {"status": "PASS" if not failures else "BLOCK", "failures": failures}
