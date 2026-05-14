from __future__ import annotations

from typing import Any

STATUS_BUILT = "BUILT_PENDING_POST_AUDIT"
NEXT_SAFE_STEP = "CONTENT_ENGINE_STRATEGY_FOUNDATION_POST_BUILD_AUDIT"


def build_strategy_state() -> dict[str, Any]:
    return {
        "project": "CONTENT_ENGINE_OMEGA",
        "layer": "CONTENT_ENGINE_STRATEGY_FOUNDATION_CORE",
        "current_status": STATUS_BUILT,
        "construction_core_status": "CLOSED_VALIDATED",
        "strategy_foundation_built": True,
        "content_generation_started": False,
        "prompt_generation_started": False,
        "script_generation_started": False,
        "queue_write_started": False,
        "metrics_write_started": False,
        "asset_write_started": False,
        "publishing_started": False,
        "execution_started": False,
        "manual_write_performed": False,
        "brain_write_performed": False,
        "reports_brain_write_performed": False,
        "n8n_performed": False,
        "webhook_performed": False,
        "capa9_performed": False,
        "next_safe_step": NEXT_SAFE_STEP,
    }


def validate_strategy_state(state: dict[str, Any]) -> dict[str, Any]:
    required_false = [
        "content_generation_started",
        "prompt_generation_started",
        "script_generation_started",
        "queue_write_started",
        "metrics_write_started",
        "asset_write_started",
        "publishing_started",
        "execution_started",
        "manual_write_performed",
        "brain_write_performed",
        "reports_brain_write_performed",
        "n8n_performed",
        "webhook_performed",
        "capa9_performed",
    ]
    failures = [key for key in required_false if state.get(key) is not False]
    if state.get("construction_core_status") != "CLOSED_VALIDATED":
        failures.append("construction_core_status")
    if state.get("next_safe_step") != NEXT_SAFE_STEP:
        failures.append("next_safe_step")
    return {"status": "PASS" if not failures else "BLOCK", "failures": failures}
