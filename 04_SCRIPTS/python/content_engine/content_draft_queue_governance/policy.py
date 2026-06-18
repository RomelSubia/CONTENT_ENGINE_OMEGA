from __future__ import annotations

from .models import QueueGovernanceDecision


class QueueGovernancePolicyError(ValueError):
    pass


ALLOWED_DECISIONS = {decision.value for decision in QueueGovernanceDecision}

FORBIDDEN_DECISIONS = {
    "QUEUE_WRITE_NOW",
    "CREATE_QUEUE_ITEM_NOW",
    "UPDATE_QUEUE_ITEM_NOW",
    "PUBLISH_NOW",
    "AUTOMATE_NOW",
    "SEND_TO_N8N",
    "TRIGGER_WEBHOOK",
    "TRIGGER_CAPA9",
    "MUTATE_MANUAL_CURRENT",
    "WRITE_BRAIN",
    "WRITE_REPORTS_BRAIN",
    "BUILD_ARGOS_BRIDGE",
}


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


def normalize_decision(decision: QueueGovernanceDecision | str) -> QueueGovernanceDecision:
    value = decision.value if isinstance(decision, QueueGovernanceDecision) else str(decision)
    if value in FORBIDDEN_DECISIONS:
        raise QueueGovernancePolicyError("FORBIDDEN_QUEUE_GOVERNANCE_DECISION")
    try:
        normalized = QueueGovernanceDecision(value)
    except ValueError as exc:
        raise QueueGovernancePolicyError("FORBIDDEN_QUEUE_GOVERNANCE_DECISION") from exc
    if normalized.value not in ALLOWED_DECISIONS:
        raise QueueGovernancePolicyError("FORBIDDEN_QUEUE_GOVERNANCE_DECISION")
    return normalized


def validate_queue_governance_policy(decision: QueueGovernanceDecision | str) -> QueueGovernanceDecision:
    return normalize_decision(decision)
