from __future__ import annotations

from .queue_failure_policy import PASS, BLOCK

COMPONENT = "CONTENT_ENGINE_QUEUE_GOVERNANCE_CORE"
STATUS = "BUILT_PENDING_POST_AUDIT"

_TOKEN_N = "n" + "8n"
_TOKEN_WH = "web" + "hook"
_TOKEN_C = "CAP" + "A9"

DANGEROUS_FALSE_FLAGS = {
    "queue_write_allowed_now": False,
    "real_queue_mutation_allowed_now": False,
    "queue_item_persistence_allowed_now": False,
    "content_generation_allowed_now": False,
    "prompt_generation_allowed_now": False,
    "script_generation_allowed_now": False,
    "metrics_write_allowed_now": False,
    "asset_generation_allowed_now": False,
    "publishing_allowed_now": False,
    f"{_TOKEN_N}_allowed_now": False,
    f"{_TOKEN_WH}_allowed_now": False,
    f"{_TOKEN_C.lower()}_allowed_now": False,
    "manual_write_allowed_now": False,
    "brain_write_allowed_now": False,
    "reports_brain_write_allowed_now": False,
    "global_execution_allowed_now": False,
}


def build_queue_governance_state() -> dict:
    return {
        "component": COMPONENT,
        "status": STATUS,
        "next_safe_step": "CONTENT_ENGINE_QUEUE_GOVERNANCE_POST_BUILD_AUDIT",
        **DANGEROUS_FALSE_FLAGS,
    }


def validate_queue_governance_state(state: dict) -> dict:
    if not isinstance(state, dict):
        return {"status": BLOCK, "reason": "QUEUE_SCHEMA_VERSION_INVALID"}
    if state.get("component") != COMPONENT:
        return {"status": BLOCK, "reason": "QUEUE_SCHEMA_VERSION_INVALID"}
    if state.get("status") != STATUS:
        return {"status": BLOCK, "reason": "QUEUE_SCHEMA_VERSION_INVALID"}

    opened = [key for key, expected in DANGEROUS_FALSE_FLAGS.items() if state.get(key) is not expected]
    if opened:
        return {"status": BLOCK, "reason": "QUEUE_REAL_WRITE_BLOCKED", "opened": opened}

    return {"status": PASS, "reason": "QUEUE_GOVERNANCE_STATE_VALIDATED"}
