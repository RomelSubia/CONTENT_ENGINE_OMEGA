from __future__ import annotations

from .models import ALLOWED_DECISIONS, FORBIDDEN_DECISIONS

MISSING_PUBLICATION_GOVERNANCE_DECISION = "MISSING_PUBLICATION_GOVERNANCE_DECISION"
FORBIDDEN_PUBLICATION_GOVERNANCE_DECISION = "FORBIDDEN_PUBLICATION_GOVERNANCE_DECISION"
UNKNOWN_PUBLICATION_GOVERNANCE_DECISION = "UNKNOWN_PUBLICATION_GOVERNANCE_DECISION"


def validate_decision(decision: str) -> tuple[bool, str | None]:
    if not decision or not decision.strip():
        return False, MISSING_PUBLICATION_GOVERNANCE_DECISION
    if decision in FORBIDDEN_DECISIONS:
        return False, FORBIDDEN_PUBLICATION_GOVERNANCE_DECISION
    if decision not in ALLOWED_DECISIONS:
        return False, UNKNOWN_PUBLICATION_GOVERNANCE_DECISION
    return True, None


def is_forbidden_operation(decision: str) -> bool:
    return decision in FORBIDDEN_DECISIONS


def blocked_operation_flags() -> dict[str, bool]:
    return {
        "publication_performed": False,
        "posting_performed": False,
        "publication_scheduled": False,
        "publication_channel_mutated": False,
        "automation_started": False,
        "n8n_started": False,
        "webhook_started": False,
        "capa9_started": False,
        "queue_write_performed": False,
        "queue_item_created": False,
        "queue_item_updated": False,
        "runtime_execution_started": False,
        "draft_creation_started": False,
        "content_generation_started": False,
        "finalization_started": False,
        "manual_current_mutation_performed": False,
        "brain_write_performed": False,
        "reports_brain_write_performed": False,
        "argos_bridge_build_performed": False,
    }
