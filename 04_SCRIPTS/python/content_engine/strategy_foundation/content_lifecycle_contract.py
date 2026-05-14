from __future__ import annotations

from typing import Any

CONCEPTUAL_STATES = [
    "IDEA",
    "SELECTED",
    "PLANNED",
    "DRAFT_READY_CONCEPTUAL",
    "REVIEW_PENDING_CONCEPTUAL",
    "APPROVED_FOR_QUEUE_FUTURE",
    "PUBLISHED_FUTURE",
    "METRICS_PENDING_FUTURE",
    "LEARNING_CAPTURED_FUTURE",
]

EXECUTION_LOCKED_STATES = [
    "QUEUE_WRITE_REAL",
    "PUBLISH_REAL",
    "METRICS_INGEST_REAL",
    "N8N_TRIGGER_REAL",
    "WEBHOOK_REAL",
    "CAPA9_REAL",
]


def build_lifecycle_contract() -> dict[str, Any]:
    return {"status": "PASS", "conceptual_states": list(CONCEPTUAL_STATES), "execution_locked_states": list(EXECUTION_LOCKED_STATES), "real_execution_allowed": False}


def validate_lifecycle_state(state: str) -> dict[str, Any]:
    if state in EXECUTION_LOCKED_STATES:
        return {"status": "BLOCK", "reason": "EXECUTION_LIFECYCLE_STATE_BLOCKED", "state": state}
    if state not in CONCEPTUAL_STATES:
        return {"status": "BLOCK", "reason": "UNKNOWN_LIFECYCLE_STATE", "state": state}
    return {"status": "PASS", "state": state}


def validate_transition(source: str, target: str) -> dict[str, Any]:
    source_result = validate_lifecycle_state(source)
    target_result = validate_lifecycle_state(target)
    if source_result["status"] != "PASS" or target_result["status"] != "PASS":
        return {"status": "BLOCK", "source": source_result, "target": target_result}
    return {"status": "PASS", "source": source, "target": target}
