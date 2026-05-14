from __future__ import annotations

from typing import Any

DANGEROUS_PERMISSIONS = {
    "content_generation_allowed_now": False,
    "prompt_generation_allowed_now": False,
    "final_script_generation_allowed_now": False,
    "script_generation_allowed_now": False,
    "asset_generation_allowed_now": False,
    "content_queue_write_allowed_now": False,
    "metrics_write_allowed_now": False,
    "monetization_allowed_now": False,
    "publishing_preparation_allowed_now": False,
    "publishing_execution_allowed_now": False,
    "manual_write_allowed_now": False,
    "brain_write_allowed_now": False,
    "reports_brain_write_allowed_now": False,
    "n8n_allowed_now": False,
    "webhook_allowed_now": False,
    "publishing_allowed_now": False,
    "capa9_allowed_now": False,
    "global_execution_allowed_now": False,
}

BLOCKED_ACTIONS = {
    "generate_script",
    "generate_post",
    "generate_video_plan",
    "final_prompt_generation",
    "write_queue",
    "write_metrics",
    "write_assets",
    "publish",
    "trigger_n8n",
    "send_webhook",
    "activate_capa9",
}


def build_boundary_plan() -> dict[str, Any]:
    return {"status": "PASS", "dangerous_permissions": dict(DANGEROUS_PERMISSIONS), "blocked_actions": sorted(BLOCKED_ACTIONS), "strategy_definition_allowed": True}


def validate_permissions(matrix: dict[str, bool] | None = None) -> dict[str, Any]:
    matrix = matrix or dict(DANGEROUS_PERMISSIONS)
    escalated = [key for key in DANGEROUS_PERMISSIONS if matrix.get(key) is not False]
    return {"status": "PASS" if not escalated else "BLOCK", "escalated": escalated}


def validate_action_allowed(action: str) -> dict[str, Any]:
    if action in BLOCKED_ACTIONS:
        return {"status": "BLOCK", "reason": "ACTION_BLOCKED_IN_STRATEGY_FOUNDATION", "action": action}
    return {"status": "PASS", "action": action}
