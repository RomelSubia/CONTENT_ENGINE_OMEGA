from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

COMPONENT = "CONTENT_DRAFT_PUBLICATION_GOVERNANCE_CORE"

REQUIRED_QUEUE_WRITE_GOVERNANCE_STATUS = "CONTENT_DRAFT_QUEUE_WRITE_GOVERNANCE_CORE_GATE_CLOSED_VALIDATED"
REQUIRED_PUBLICATION_READINESS_MAP_STATUS = "NEXT_LAYER_READINESS_MAP_AFTER_CONTENT_DRAFT_QUEUE_WRITE_GOVERNANCE_DEFINED"

READY_STATUS = "READY_FOR_PUBLICATION_EXECUTION_GOVERNANCE_PLAN_ONLY"
FAILED_STATUS = "FAILED_CLOSED"

ALLOWED_DECISIONS = (
    "AUTHORIZE_PUBLICATION_GOVERNANCE_PLAN_ONLY",
    "REQUEST_REVISION_BEFORE_PUBLICATION",
    "REJECT_PUBLICATION_READINESS",
    "HOLD_PUBLICATION_READINESS",
    "ESCALATE_PUBLICATION_REVIEW",
)

FORBIDDEN_DECISIONS = (
    "PUBLISH_NOW",
    "POST_NOW",
    "SCHEDULE_PUBLICATION_NOW",
    "UPDATE_PUBLICATION_CHANNEL_NOW",
    "TRIGGER_N8N_NOW",
    "TRIGGER_WEBHOOK_NOW",
    "TRIGGER_CAPA9_NOW",
    "AUTOMATE_NOW",
    "WRITE_QUEUE_NOW",
    "CREATE_QUEUE_ITEM_NOW",
    "UPDATE_QUEUE_ITEM_NOW",
    "GENERATE_CONTENT_NOW",
    "FINALIZE_CONTENT_NOW",
    "MUTATE_MANUAL_CURRENT_NOW",
    "WRITE_BRAIN_NOW",
    "WRITE_REPORTS_BRAIN_NOW",
    "BUILD_ARGOS_BRIDGE_NOW",
)


@dataclass(frozen=True)
class PublicationGovernanceEvidence:
    queue_write_governance_gate_close_reference: str
    queue_write_governance_gate_close_sha256: str
    queue_write_governance_status: str
    publication_readiness_map_reference: str
    publication_readiness_map_sha256: str
    publication_readiness_map_status: str
    safe_preview_reference: str
    safe_preview_sha256: str
    human_review_reference: str
    human_review_sha256: str
    finalization_reference: str
    finalization_sha256: str
    safe_preview_status: str = "AVAILABLE_OR_EXPLICITLY_NOT_REQUIRED_BY_POLICY"
    human_review_status: str = "APPROVED_OR_ESCALATED_FOR_PUBLICATION_GOVERNANCE_ONLY"
    finalization_status: str = "FINALIZATION_GOVERNANCE_CLOSED_OR_PLAN_ONLY_REFERENCE"


@dataclass(frozen=True)
class PublicationGovernanceRequest:
    request_id: str
    operator_identity: str
    policy_version: str
    timestamp: str
    target_publication_channel: str
    publication_intent: str
    idempotency_key: str
    decision: str
    evidence: PublicationGovernanceEvidence


@dataclass(frozen=True)
class PublicationIntent:
    request_id: str
    target_publication_channel: str
    publication_intent: str
    plan_only: bool = True
    publication_performed: bool = False
    posting_performed: bool = False
    publication_scheduled: bool = False
    publication_channel_mutated: bool = False
    automation_started: bool = False
    n8n_started: bool = False
    webhook_started: bool = False
    capa9_started: bool = False
    queue_write_performed: bool = False
    queue_item_created: bool = False
    queue_item_updated: bool = False
    runtime_execution_started: bool = False


@dataclass(frozen=True)
class PublicationGovernanceResult:
    request_id: str
    publication_governance_status: str
    errors: tuple[str, ...] = field(default_factory=tuple)
    result_is_plan_only: bool = True
    publication_performed: bool = False
    posting_performed: bool = False
    publication_scheduled: bool = False
    publication_channel_mutated: bool = False
    automation_started: bool = False
    n8n_started: bool = False
    webhook_started: bool = False
    capa9_started: bool = False
    queue_write_performed: bool = False
    queue_item_created: bool = False
    queue_item_updated: bool = False
    runtime_execution_started: bool = False


@dataclass(frozen=True)
class PublicationAuditRecord:
    component: str
    request_id: str
    operator_identity: str
    decision: str
    status: str
    errors: tuple[str, ...]
    blocked_operation_flags: dict[str, bool]
    metadata: dict[str, Any] = field(default_factory=dict)
