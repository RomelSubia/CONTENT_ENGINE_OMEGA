from __future__ import annotations

from typing import Any

PROJECT = "CONTENT_ENGINE_OMEGA"
PHASE = "CONTENT_ENGINE_CONSTRUCTION"
CONSUMED_BRIDGE_STATUS = "MANUAL_CEREBRO_BRIDGE_CLOSED_VALIDATED"
STATUS_BUILT_PENDING_POST_AUDIT = "BUILT_PENDING_POST_AUDIT"
NEXT_SAFE_STEP = "CONTENT_ENGINE_CONSTRUCTION_POST_BUILD_AUDIT"

BLOCKED_ACTIONS = [
    "CONTENT_ENGINE_EXECUTION",
    "CONTENT_GENERATION",
    "ASSET_GENERATION",
    "QUEUE_WRITE",
    "METRICS_WRITE",
    "MONETIZATION",
    "PUBLISHING_PREPARATION",
    "PUBLISHING_EXECUTION",
    "MANUAL_WRITE",
    "BRAIN_WRITE",
    "REPORTS_BRAIN_WRITE",
    "N8N",
    "WEBHOOK",
    "CAPA9",
]


def build_state() -> dict[str, Any]:
    return {
        "project": PROJECT,
        "phase": PHASE,
        "component": "CONTENT_ENGINE_CONSTRUCTION_CORE",
        "current_status": STATUS_BUILT_PENDING_POST_AUDIT,
        "consumed_bridge_status": CONSUMED_BRIDGE_STATUS,
        "construction_core_built": True,
        "execution_started": False,
        "manual_write_performed": False,
        "brain_write_performed": False,
        "reports_brain_write_performed": False,
        "n8n_performed": False,
        "webhook_performed": False,
        "publishing_performed": False,
        "capa9_performed": False,
        "next_safe_step": NEXT_SAFE_STEP,
        "blocked_actions": list(BLOCKED_ACTIONS),
    }


def validate_state(state: dict[str, Any]) -> dict[str, Any]:
    required_false = [
        "execution_started",
        "manual_write_performed",
        "brain_write_performed",
        "reports_brain_write_performed",
        "n8n_performed",
        "webhook_performed",
        "publishing_performed",
        "capa9_performed",
    ]
    failures = [key for key in required_false if state.get(key) is not False]
    if state.get("consumed_bridge_status") != CONSUMED_BRIDGE_STATUS:
        failures.append("consumed_bridge_status")
    if state.get("next_safe_step") != NEXT_SAFE_STEP:
        failures.append("next_safe_step")
    return {"status": "PASS" if not failures else "BLOCK", "failures": failures}
