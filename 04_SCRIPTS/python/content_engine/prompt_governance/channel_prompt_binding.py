from __future__ import annotations

from typing import Any

CANONICAL_CHANNEL_IDS = [
    "CHANNEL_A_MONEY_MINDSET_CONVERSION",
    "CHANNEL_D_AI_TECH_PERSONAL_BRAND",
    "CHANNEL_B_CURIOSITIES_MASS_TRAFFIC",
    "CHANNEL_C_MOTIVATION_DISCIPLINE_RETENTION",
]

AMBIGUOUS_ALIASES = {"channel_1", "money", "viral", "tech", "motivation", "general", "all_channels", "universal", "multi_channel"}

REQUIRED_FIELDS = [
    "prompt_id",
    "prompt_type",
    "channel_id",
    "prompt_intent",
    "allowed_tone",
    "blocked_tone",
    "allowed_output_shape",
    "blocked_output_shape",
    "pillar_reference",
    "audience_reference",
    "quality_rules",
    "safety_rules",
]


def validate_channel_id(channel_id: str | None) -> dict[str, Any]:
    if not channel_id:
        return {"status": "BLOCK", "reason": "PROMPT_WITHOUT_CHANNEL"}
    if channel_id in AMBIGUOUS_ALIASES:
        return {"status": "BLOCK", "reason": "AMBIGUOUS_CHANNEL_ALIAS", "channel_id": channel_id}
    if channel_id not in CANONICAL_CHANNEL_IDS:
        return {"status": "BLOCK", "reason": "UNKNOWN_CHANNEL_ID", "channel_id": channel_id}
    return {"status": "PASS", "channel_id": channel_id}


def validate_channel_prompt_binding(payload: dict[str, Any]) -> dict[str, Any]:
    channel_result = validate_channel_id(payload.get("channel_id"))
    if channel_result["status"] != "PASS":
        return channel_result
    missing = [field for field in REQUIRED_FIELDS if payload.get(field) in (None, "", [])]
    return {"status": "PASS" if not missing else "BLOCK", "reason": "MISSING_PROMPT_BINDING_FIELDS" if missing else None, "missing": missing}
