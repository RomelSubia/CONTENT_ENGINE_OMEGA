from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


COMPONENT = "CONTENT_DRAFT_PUBLICATION_EXECUTION_GOVERNANCE_CORE"

BLOCKED_DECISION = "BLOCKED_PUBLICATION_EXECUTION_GOVERNANCE_FAIL_CLOSED"
PLAN_ONLY_DECISION = "PLAN_ONLY_PUBLICATION_EXECUTION_GOVERNANCE_VALIDATED_NO_EXECUTION"

REQUIRED_FIELDS = (
    "request_id",
    "draft_id",
    "queue_item_id",
    "publication_governance_seal",
    "operator_authorization_status",
    "channel_policy_status",
    "dry_run_required",
)


@dataclass(frozen=True)
class PublicationExecutionGovernanceInput:
    request_id: str | None = None
    draft_id: str | None = None
    queue_item_id: str | None = None
    publication_governance_seal: Mapping[str, Any] | None = None
    operator_authorization_status: str | None = None
    channel_policy_status: str | None = None
    dry_run_required: bool = True
    notes: str | None = None
    risk_context: Mapping[str, Any] | None = None
    channel_candidate: str | None = None


@dataclass(frozen=True)
class PublicationExecutionGovernanceResult:
    component: str = COMPONENT
    status: str = "BLOCKED_FAIL_CLOSED"
    decision: str = BLOCKED_DECISION
    publication_execution_allowed_now: bool = False
    publishing_allowed_now: bool = False
    posting_allowed_now: bool = False
    publication_scheduling_allowed_now: bool = False
    publication_channel_mutation_allowed_now: bool = False
    runtime_execution_allowed_now: bool = False
    queue_write_allowed_now: bool = False
    queue_item_creation_allowed_now: bool = False
    queue_item_update_allowed_now: bool = False
    automation_allowed_now: bool = False
    n8n_allowed_now: bool = False
    webhook_allowed_now: bool = False
    capa9_allowed_now: bool = False
    source_files_written: bool = False
    test_files_written: bool = False
    publication_execution_started: bool = False
    publishing_started: bool = False
    posting_started: bool = False
    publication_scheduling_started: bool = False
    publication_channel_mutation_started: bool = False
    automation_started: bool = False
    queue_write_performed: bool = False
    queue_item_created: bool = False
    queue_item_updated: bool = False
    reasons: tuple[str, ...] = field(default_factory=tuple)
    evidence_summary: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "status": self.status,
            "decision": self.decision,
            "publication_execution_allowed_now": self.publication_execution_allowed_now,
            "publishing_allowed_now": self.publishing_allowed_now,
            "posting_allowed_now": self.posting_allowed_now,
            "publication_scheduling_allowed_now": self.publication_scheduling_allowed_now,
            "publication_channel_mutation_allowed_now": self.publication_channel_mutation_allowed_now,
            "runtime_execution_allowed_now": self.runtime_execution_allowed_now,
            "queue_write_allowed_now": self.queue_write_allowed_now,
            "queue_item_creation_allowed_now": self.queue_item_creation_allowed_now,
            "queue_item_update_allowed_now": self.queue_item_update_allowed_now,
            "automation_allowed_now": self.automation_allowed_now,
            "n8n_allowed_now": self.n8n_allowed_now,
            "webhook_allowed_now": self.webhook_allowed_now,
            "capa9_allowed_now": self.capa9_allowed_now,
            "source_files_written": self.source_files_written,
            "test_files_written": self.test_files_written,
            "publication_execution_started": self.publication_execution_started,
            "publishing_started": self.publishing_started,
            "posting_started": self.posting_started,
            "publication_scheduling_started": self.publication_scheduling_started,
            "publication_channel_mutation_started": self.publication_channel_mutation_started,
            "automation_started": self.automation_started,
            "queue_write_performed": self.queue_write_performed,
            "queue_item_created": self.queue_item_created,
            "queue_item_updated": self.queue_item_updated,
            "reasons": list(self.reasons),
            "evidence_summary": dict(self.evidence_summary),
        }


class ContentDraftPublicationExecutionGovernanceCore:
    def evaluate(
        self,
        request: PublicationExecutionGovernanceInput | Mapping[str, Any] | None,
    ) -> PublicationExecutionGovernanceResult:
        normalized = self._normalize(request)
        missing = self._missing_fields(normalized)

        reasons: list[str] = []
        if missing:
            reasons.append("missing_required_evidence:" + ",".join(missing))

        if normalized.dry_run_required is not True:
            reasons.append("dry_run_required_must_remain_true")

        if normalized.operator_authorization_status != "approved_for_plan_only":
            reasons.append("operator_authorization_not_approved_for_plan_only")

        if normalized.channel_policy_status != "validated_for_plan_only":
            reasons.append("channel_policy_not_validated_for_plan_only")

        seal_status = ""
        if isinstance(normalized.publication_governance_seal, Mapping):
            seal_status = str(normalized.publication_governance_seal.get("sealed_status", ""))

        if not seal_status:
            reasons.append("publication_governance_seal_missing_status")

        evidence_summary = {
            "request_id_present": bool(normalized.request_id),
            "draft_id_present": bool(normalized.draft_id),
            "queue_item_id_present": bool(normalized.queue_item_id),
            "publication_governance_seal_status": seal_status,
            "operator_authorization_status": normalized.operator_authorization_status,
            "channel_policy_status": normalized.channel_policy_status,
            "dry_run_required": normalized.dry_run_required,
            "channel_candidate_present": bool(normalized.channel_candidate),
        }

        if reasons:
            return PublicationExecutionGovernanceResult(
                status="BLOCKED_FAIL_CLOSED",
                decision=BLOCKED_DECISION,
                reasons=tuple(reasons),
                evidence_summary=evidence_summary,
            )

        return PublicationExecutionGovernanceResult(
            status="VALIDATED_PLAN_ONLY_EXECUTION_BLOCKED",
            decision=PLAN_ONLY_DECISION,
            reasons=(
                "publication_execution_governance_validated_for_plan_only",
                "productive_execution_requires_future_gate",
            ),
            evidence_summary=evidence_summary,
        )

    def _normalize(
        self,
        request: PublicationExecutionGovernanceInput | Mapping[str, Any] | None,
    ) -> PublicationExecutionGovernanceInput:
        if request is None:
            return PublicationExecutionGovernanceInput()

        if isinstance(request, PublicationExecutionGovernanceInput):
            return request

        if isinstance(request, Mapping):
            return PublicationExecutionGovernanceInput(
                request_id=self._as_optional_str(request.get("request_id")),
                draft_id=self._as_optional_str(request.get("draft_id")),
                queue_item_id=self._as_optional_str(request.get("queue_item_id")),
                publication_governance_seal=self._as_optional_mapping(request.get("publication_governance_seal")),
                operator_authorization_status=self._as_optional_str(request.get("operator_authorization_status")),
                channel_policy_status=self._as_optional_str(request.get("channel_policy_status")),
                dry_run_required=bool(request.get("dry_run_required", True)),
                notes=self._as_optional_str(request.get("notes")),
                risk_context=self._as_optional_mapping(request.get("risk_context")),
                channel_candidate=self._as_optional_str(request.get("channel_candidate")),
            )

        return PublicationExecutionGovernanceInput()

    def _missing_fields(self, request: PublicationExecutionGovernanceInput) -> tuple[str, ...]:
        missing: list[str] = []
        for field_name in REQUIRED_FIELDS:
            value = getattr(request, field_name)
            if value is None:
                missing.append(field_name)
        return tuple(missing)

    def _as_optional_str(self, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _as_optional_mapping(self, value: Any) -> Mapping[str, Any] | None:
        if isinstance(value, Mapping):
            return value
        return None


def evaluate_publication_execution_governance(
    request: PublicationExecutionGovernanceInput | Mapping[str, Any] | None,
) -> PublicationExecutionGovernanceResult:
    return ContentDraftPublicationExecutionGovernanceCore().evaluate(request)
