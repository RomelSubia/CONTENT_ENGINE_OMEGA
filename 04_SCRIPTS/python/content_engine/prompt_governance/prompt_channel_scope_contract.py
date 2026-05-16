from __future__ import annotations

from typing import Any

from .channel_prompt_binding import CANONICAL_CHANNEL_IDS, validate_channel_id


def validate_prompt_channel_scope(payload: dict[str, Any]) -> dict[str, Any]:
    channel_result = validate_channel_id(payload.get("channel_id"))
    if channel_result["status"] != "PASS":
        return channel_result

    channels = payload.get("channel_ids")
    if payload.get("universal_prompt") is True:
        return {"status": "BLOCK", "reason": "UNIVERSAL_PROMPT_BLOCKED"}
    if channels and len(channels) > 1 and not payload.get("bridge_rule"):
        return {"status": "BLOCK", "reason": "MULTI_CHANNEL_WITHOUT_BRIDGE_RULE"}
    if any(channel not in CANONICAL_CHANNEL_IDS for channel in channels or [payload.get("channel_id")]):
        return {"status": "BLOCK", "reason": "UNKNOWN_CHANNEL_IN_SCOPE"}
    if payload.get("mixes_channel_tones") is True or payload.get("mixes_channel_audiences") is True or payload.get("mixes_channel_pillars") is True:
        return {"status": "BLOCK", "reason": "CROSS_CHANNEL_CONTAMINATION"}
    return {"status": "PASS", "channel_id": payload.get("channel_id")}
