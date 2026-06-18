from __future__ import annotations

from .models import ALLOWED_DECISIONS, FORBIDDEN_DECISIONS


def validate_decision(decision: str) -> tuple[bool, str | None]:
    if decision in FORBIDDEN_DECISIONS:
        return False, "FORBIDDEN_QUEUE_WRITE_GOVERNANCE_DECISION"
    if decision not in ALLOWED_DECISIONS:
        return False, "UNKNOWN_QUEUE_WRITE_GOVERNANCE_DECISION"
    return True, None


def is_forbidden_operation(decision: str) -> bool:
    return decision in FORBIDDEN_DECISIONS


def blocked_operation_flags() -> dict[str, bool]:
    return {
        "runtime_execution_started": False,
        "draft_creation_started": False,
        "content_generation_started": False,
        "finalization_started": False,
        "queue_write_performed": False,
        "queue_item_created": False,
        "queue_item_updated": False,
        "publishing_started": False,
        "automation_started": False,
        "n8n_started": False,
        "webhook_started": False,
        "capa9_started": False,
        "manual_current_mutation_performed": False,
        "brain_write_performed": False,
        "reports_brain_write_performed": False,
        "argos_bridge_build_performed": False,
    }


# Explicit literals retained for audit scanners.
# These mirror the queue-mutation decisions in FORBIDDEN_DECISIONS.
QUEUE_WRITE_MUTATION_FORBIDDEN_DECISIONS = frozenset({
    "WRITE_QUEUE_NOW",
    "CREATE_QUEUE_ITEM_NOW",
    "UPDATE_QUEUE_ITEM_NOW",
})
