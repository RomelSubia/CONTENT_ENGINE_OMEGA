from __future__ import annotations

from typing import Any

from .channel_registry import validate_channel_id
from .channel_separation_matrix import validate_channel_mix


def validate_channel_payload(channel_id: str, target_channel_id: str | None = None, has_bridge_rule: bool = False) -> dict[str, Any]:
    channel_check = validate_channel_id(channel_id)
    if channel_check["status"] != "PASS":
        return channel_check
    if target_channel_id is not None:
        target_check = validate_channel_id(target_channel_id)
        if target_check["status"] != "PASS":
            return target_check
        return validate_channel_mix(channel_id, target_channel_id, has_bridge_rule)
    return {"status": "PASS", "channel_id": channel_id}


def block_productive_prompt(prompt_type: str) -> dict[str, Any]:
    blocked = {"final_script_prompt", "viral_video_prompt", "publishing_caption_prompt", "production_prompt_pack", "ready_to_publish_script", "ready_to_record_script"}
    if prompt_type in blocked:
        return {"status": "BLOCK", "reason": "PRODUCTIVE_PROMPT_BLOCKED"}
    return {"status": "PASS", "prompt_type": prompt_type}
