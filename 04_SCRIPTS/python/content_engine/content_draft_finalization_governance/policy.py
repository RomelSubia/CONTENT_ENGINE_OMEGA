from __future__ import annotations

from .models import FinalizationDecision


class FinalizationPolicyError(ValueError):
    """Raised when a finalization request violates governance policy."""


class FinalizationPolicy:
    allowed_decisions = {
        FinalizationDecision.FINALIZE_FOR_QUEUE_GOVERNANCE_PLAN_ONLY,
        FinalizationDecision.REQUEST_REVISION_BEFORE_FINALIZATION,
        FinalizationDecision.REJECT_FINALIZATION,
        FinalizationDecision.HOLD_FINALIZATION,
        FinalizationDecision.ESCALATE_FINALIZATION_REVIEW,
    }

    forbidden_decision_values = {
        "PUBLISH_NOW",
        "QUEUE_WRITE_NOW",
        "AUTOMATE_NOW",
        "SEND_TO_N8N",
        "TRIGGER_WEBHOOK",
        "TRIGGER_CAPA9",
        "MUTATE_MANUAL_CURRENT",
        "WRITE_BRAIN",
        "BUILD_ARGOS_BRIDGE",
    }

    @classmethod
    def assert_allowed_decision(cls, decision: FinalizationDecision | str) -> FinalizationDecision:
        if isinstance(decision, str):
            if decision in cls.forbidden_decision_values:
                raise FinalizationPolicyError(f"FORBIDDEN_DECISION: {decision}")
            try:
                decision = FinalizationDecision(decision)
            except ValueError as exc:
                raise FinalizationPolicyError(f"UNKNOWN_DECISION: {decision}") from exc

        if decision not in cls.allowed_decisions:
            raise FinalizationPolicyError(f"DECISION_NOT_ALLOWED: {decision}")

        return decision

    @classmethod
    def blocked_operation_flags(cls) -> dict[str, bool]:
        return {
            "runtime_execution_started": False,
            "draft_creation_started": False,
            "content_generation_started": False,
            "finalization_started": False,
            "queue_write_performed": False,
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
