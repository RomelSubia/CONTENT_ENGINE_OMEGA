from __future__ import annotations

from typing import Any

BLOCKED_ACTIONS = {
    "generate_now",
    "write_final_script",
    "create_publishable_post",
    "send_to_queue",
    "write_metrics",
    "create_asset",
    "upload_video",
    "publish_now",
    "trigger_n8n",
    "call_webhook",
    "activate_capa9",
    "write_manual",
    "write_brain",
    "write_reports_brain",
}


def validate_prompt_safety_action(action: str) -> dict[str, Any]:
    if action in BLOCKED_ACTIONS:
        return {"status": "BLOCK", "reason": "PROMPT_SAFETY_VIOLATION", "action": action}
    return {"status": "PASS", "action": action}
